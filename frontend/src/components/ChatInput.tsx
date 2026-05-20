import { useState, useRef, useCallback } from 'react'
import { useTripStore } from '@/stores/tripStore'
import { useConversationStore } from '@/stores/conversationStore'
import { useProfileStore } from '@/stores/profileStore'

interface ChatInputProps {
  send: (type: string, payload: Record<string, unknown>) => void
}

export function ChatInput({ send }: ChatInputProps) {
  const [text, setText] = useState('')
  const [selectedSeat, setSelectedSeat] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const tripId = useTripStore((s) => s.tripId)
  const addMessage = useConversationStore((s) => s.addMessage)
  const vehicleProfiles = useProfileStore((s) => s.vehicleProfiles)
  const seatOccupancy = useTripStore((s) => s.seatOccupancy)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim() || !tripId) return
    sendUtterance(text.trim())
    setText('')
  }

  const sendUtterance = useCallback((transcript: string) => {
    const actor = seatOccupancy[selectedSeat]
    const actorId = actor?.actor_id ?? `spk_${selectedSeat}`

    addMessage({
      id: `msg-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
      type: 'utterance',
      actor_id: actorId,
      text: transcript,
      timestamp: new Date().toISOString(),
    })

    send('utterance', {
      trip_id: tripId,
      spk_label: `spk_${selectedSeat}`,
      transcript,
      seat_channel: selectedSeat,
    })
  }, [seatOccupancy, selectedSeat, tripId, addMessage, send])

  const toggleMic = useCallback(() => {
    if (isRecording) {
      recognitionRef.current?.stop()
      setIsRecording(false)
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('이 브라우저는 음성 인식을 지원하지 않습니다.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'ko-KR'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript
      sendUtterance(transcript)
      setIsRecording(false)
    }

    recognition.onerror = () => setIsRecording(false)
    recognition.onend = () => setIsRecording(false)

    recognitionRef.current = recognition
    recognition.start()
    setIsRecording(true)
  }, [isRecording, sendUtterance])

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-center pt-2 border-t border-gray-700">
      <select
        value={selectedSeat}
        onChange={(e) => setSelectedSeat(Number(e.target.value))}
        className="bg-gray-700 text-xs rounded px-2 py-2 border border-gray-600"
        aria-label="좌석 선택"
      >
        {vehicleProfiles.map((p) => (
          <option key={p.default_seat_channel} value={p.default_seat_channel ?? 0}>
            {p.name}
          </option>
        ))}
      </select>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="발화를 입력하세요..."
        className="flex-1 bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
        aria-label="발화 입력"
      />
      <button
        type="button"
        onClick={toggleMic}
        className={`px-3 py-2 rounded text-sm transition-colors ${
          isRecording ? 'bg-red-600 animate-pulse' : 'bg-gray-700 hover:bg-gray-600'
        }`}
        aria-label={isRecording ? '녹음 중지' : '음성 입력'}
      >
        🎤
      </button>
      <button
        type="submit"
        disabled={!text.trim()}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 rounded text-sm transition-colors"
      >
        전송
      </button>
    </form>
  )
}
