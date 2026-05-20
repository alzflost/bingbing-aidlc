import { useEffect, useRef, useCallback, useState } from 'react'
import { useTripStore } from '@/stores/tripStore'
import { useConversationStore } from '@/stores/conversationStore'
import { useProfileStore } from '@/stores/profileStore'
import {
  WsMessageSchema,
  ConversationMessageSchema,
  MappingUpdatePayloadSchema,
  StateUpdatePayloadSchema,
  PermissionUpdatePayloadSchema,
} from '@/types/schemas'

export function useWebSocket(url: string) {
  const wsRef = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const updateMapping = useTripStore((s) => s.updateMapping)
  const updateState = useTripStore((s) => s.updateState)
  const addMessage = useConversationStore((s) => s.addMessage)
  const updatePermissions = useProfileStore((s) => s.updatePermissions)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)

    ws.onclose = () => {
      setConnected(false)
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => ws.close()

    ws.onmessage = (event) => {
      // SECURITY-05: Validate all incoming messages with Zod
      const raw = JSON.parse(event.data as string)
      const parsed = WsMessageSchema.safeParse(raw)
      if (!parsed.success) {
        console.warn('[WS] Invalid message received:', parsed.error.issues)
        return
      }

      const msg = parsed.data
      switch (msg.type) {
        case 'transcription': {
          const result = ConversationMessageSchema.safeParse(msg.payload)
          if (result.success) {
            addMessage({ ...result.data, type: 'utterance' })
          }
          break
        }
        case 'agent_response': {
          const result = ConversationMessageSchema.safeParse(msg.payload)
          if (result.success) {
            addMessage({ ...result.data, type: 'agent_response' })
          }
          break
        }
        case 'mapping_update': {
          const result = MappingUpdatePayloadSchema.safeParse(msg.payload)
          if (result.success) {
            updateMapping(result.data.spk_label, result.data.actor_id)
          }
          break
        }
        case 'state_update': {
          const result = StateUpdatePayloadSchema.safeParse(msg.payload)
          if (result.success) {
            updateState(result.data.state)
          }
          break
        }
        case 'permission_update': {
          const result = PermissionUpdatePayloadSchema.safeParse(msg.payload)
          if (result.success) {
            updatePermissions(result.data.actor_id, result.data.permissions)
          }
          break
        }
      }
    }
  }, [url, addMessage, updateMapping, updateState, updatePermissions])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const send = useCallback((type: string, payload: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }))
    }
  }, [])

  const sendTripStart = useCallback(
    (vehicleId: string, seatData: Record<number, string | null>, driverActorId: string) => {
      send('trip_start', { vehicle_id: vehicleId, seat_occupancy: seatData, driver_actor_id: driverActorId })
    },
    [send]
  )

  const sendTripEnd = useCallback(() => {
    send('trip_end', {})
  }, [send])

  const sendAudio = useCallback((chunk: ArrayBuffer) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(chunk)
    }
  }, [])

  return { connected, send, sendTripStart, sendTripEnd, sendAudio }
}
