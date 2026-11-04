---
id: 25
title: "Profile Page - User Profile Management"
priority: medium
type: feature
agent: frontend
sprint: 2
estimate: S
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #25: Profile Page - User Profile Management

## Description
Replace the `ComingSoon` placeholder in `frontend/src/pages/Profile.tsx` with a complete user profile management page.

## Acceptance Criteria

### Profile View
- [ ] Display current user info: Name, Email, Role, Company, Status, Created At
- [ ] Avatar with upload/change option (uses existing Avatar component)
- [ ] Role display with badge (using `getStatusBadge` or similar)

### Edit Profile
- [ ] "Edit Profile" button opens modal/form
- [ ] Editable fields: Name, Email, Phone, Avatar
- [ ] Non-editable: Role, Company, Status (admin only)
- [ ] Form validation with React Hook Form + Zod
- [ ] On submit: PATCH `/api/v1/users/me` (self-update endpoint)

### Change Password
- [ ] "Change Password" section/button
- [ ] Modal with: Current Password, New Password, Confirm New Password
- [ ] Password strength indicator
- [ ] Validation: current password correct, new password meets requirements
- [ ] On submit: POST `/api/v1/auth/change-password` (or similar endpoint)

### Notification Preferences
- [ ] Section for notification preferences
- [ ] Toggle switches for: Email notifications, In-app notifications, Weekly reports, Discrepancy alerts, Contest updates
- [ ] Per-channel preferences (Email, Push, SMS if available)
- [ ] On save: PATCH `/api/v1/notifications/preferences`

### Account Actions (Danger Zone)
- [ ] "Delete Account" button (with confirmation modal)
- [ ] Requires password confirmation
- [ ] Calls DELETE `/api/v1/users/me` (soft delete or admin only)

## Technical Requirements

### API Endpoints
```typescript
// User profile
GET /api/v1/users/me
PATCH /api/v1/users/me

// Password
POST /api/v1/auth/change-password

// Notifications
GET /api/v1/notifications/preferences
PATCH /api/v1/notifications/preferences

// Avatar upload (if supported)
POST /api/v1/users/me/avatar
```

### Components to Create
- `src/components/profile/ProfileHeader.tsx` - Avatar, name, role, company
- `src/components/profile/ProfileForm.tsx` - Edit profile form
- `src/components/profile/ChangePasswordModal.tsx` - Password change modal
- `src/components/profile/NotificationPreferences.tsx` - Toggle switches
- `src/components/profile/DangerZone.tsx` - Delete account section

### Hooks to Create (delegate to state-agent)
- `useCurrentUser()` - TanStack Query for current user
- `useUpdateProfile()` - Update profile mutation
- `useChangePassword()` - Change password mutation
- `useNotificationPreferences()` - Preferences query
- `useUpdateNotificationPreferences()` - Update preferences mutation
- `useUploadAvatar()` - Avatar upload mutation (if supported)

### Zod Schemas (delegate to state-agent)
```typescript
const profileSchema = z.object({
  name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  email: z.string().email("Email inválido"),
  phone: z.string().optional(),
});

const changePasswordSchema = z.object({
  current_password: z.string().min(1, "Senha atual obrigatória"),
  new_password: z.string().min(8, "Nova senha deve ter pelo menos 8 caracteres"),
  confirm_password: z.string(),
}).refine(data => data.new_password === data.confirm_password, {
  message: "Senhas não coincidem",
  path: ["confirm_password"],
});

const notificationPreferencesSchema = z.object({
  email_enabled: z.boolean(),
  in_app_enabled: z.boolean(),
  weekly_report: z.boolean(),
  discrepancy_alerts: z.boolean(),
  contest_updates: z.boolean(),
});
```

## Dependencies
- Card #01: Testing infrastructure (DONE)
- Card #07: Design System (Toggle, Avatar - mostly done)
- Backend: User/Notification endpoints already implemented

## Design References
- `frontend/src/index.css` - Forms, Cards, Badges
- `frontend/src/components/Avatar.tsx` - Use existing Avatar component
- `frontend/src/components/Modal.tsx` - Modal wrapper
- `frontend/src/utils/helpers.ts` - `getStatusBadge` for role display

## Testing Requirements
- Unit tests for form validation
- Integration tests for profile update, password change
- MSW handlers for all profile endpoints
- Accessibility tests

## Definition of Done
- [ ] Profile displays current user info correctly
- [ ] Edit profile works with validation
- [ ] Change password works with current password verification
- [ ] Notification preferences toggles work and persist
- [ ] Danger zone: delete account works with confirmation
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] Tests written and passing
- [ ] Card moved to `review/`

## Notes
- Backend user/notification endpoints are already implemented per `backend/README.md`
- Simple page - good for Sprint 2 completion
- Role/Company are read-only for non-admin users
- Avatar upload: check if backend supports it, otherwise use placeholder