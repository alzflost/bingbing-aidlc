// Family Car Agent — CEDAR Policies
// Role-based permission rules

// === PERMIT Rules ===

// Driver (adult) has full access to all tools
permit(
    principal,
    action,
    resource
) when {
    principal.driver == true &&
    principal.age_group == "adult"
};

// Adult family passenger: all except vehicle driving control
permit(
    principal,
    action,
    resource
) when {
    principal.driver == false &&
    principal.age_group == "adult" &&
    principal.relationship in ["owner", "family"] &&
    action != Action::"vehicle_drive_control"
};

// Elder: seat control + music + web search always allowed
permit(
    principal,
    action,
    resource
) when {
    principal.age_group == "elder" &&
    action in [Action::"seat_control", Action::"music", Action::"web_search"]
};

// Elder: phone call with confirmation
permit(
    principal,
    action,
    resource
) when {
    principal.age_group == "elder" &&
    action == Action::"bt_call" &&
    context.confirmation_received == true
};

// Child: music with age filter and volume limit
permit(
    principal,
    action,
    resource
) when {
    principal.age_group == "child" &&
    action == Action::"music" &&
    context.content_age_appropriate == true &&
    context.volume_percent <= 60
};

// Child: web search with content filter
permit(
    principal,
    action,
    resource
) when {
    principal.age_group == "child" &&
    action == Action::"web_search" &&
    context.content_filtered == true
};

// Child: seat control only when stopped
permit(
    principal,
    action,
    resource
) when {
    principal.age_group == "child" &&
    action == Action::"seat_control" &&
    context.driving_speed == 0 &&
    context.parent_confirmed == true
};

// Guest: only web search (info queries)
permit(
    principal,
    action,
    resource
) when {
    principal.relationship == "guest" &&
    action == Action::"web_search"
};

// === FORBID Rules ===

// Children cannot use vehicle control, navigation, or phone
forbid(
    principal,
    action,
    resource
) when {
    principal.age_group == "child" &&
    action in [Action::"vehicle_drive_control", Action::"navigation", Action::"bt_call"]
};

// Children cannot control seat while driving fast
forbid(
    principal,
    action,
    resource
) when {
    principal.age_group == "child" &&
    action == Action::"seat_control" &&
    context.driving_speed > 0
} unless {
    context.parent_confirmed == true &&
    context.driving_speed == 0
};

// Guest cannot use any control tools
forbid(
    principal,
    action,
    resource
) when {
    principal.relationship == "guest" &&
    action != Action::"web_search"
};

// Elder cannot use navigation or vehicle drive control
forbid(
    principal,
    action,
    resource
) when {
    principal.age_group == "elder" &&
    action in [Action::"vehicle_drive_control", Action::"navigation"]
};
