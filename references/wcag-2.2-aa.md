# WCAG 2.2 Level AA Release Profile

## Contents

1. [Conformance contract](#conformance-contract)
2. [Input and focus](#input-and-focus)
3. [Forms and input assistance](#forms-and-input-assistance)
4. [Authentication and account recovery](#authentication-and-account-recovery)
5. [Timing and session expiry](#timing-and-session-expiry)
6. [Moving and live information](#moving-and-live-information)
7. [Audio, video, flashes, and orientation](#audio-video-flashes-and-orientation)
8. [Public accountability](#public-accountability)
9. [Normative and implementation references](#normative-and-implementation-references)

## Conformance contract

WCAG 2.2 Level AA is the minimum release target for every Swarma surface: product website
and web application. It includes all Level A and Level AA success criteria.

Apply the target to:

- Every route needed to discover, understand, purchase, configure, operate, and obtain
  support for the product.
- Authentication, account recovery, consent, checkout, destructive actions, and other
  multi-step processes.
- Default, loading, empty, error, offline, permission-denied, expired, success, and live
  states.
- Mobile and desktop layouts, every supported language and direction, and required
  third-party content in the conforming process.

A release may ship with a known exception only when the owner records the affected
criterion, user impact, accessible alternative, responsible person, and remediation
date. Publish the limitation. Do not call the product fully conformant while an
exception remains.

WCAG is the minimum. Keep stronger family rules such as 44px targets, reduced-motion
alternatives, and reduced-transparency support even where the standard permits less.

## Input and focus

- Every function has a keyboard path and does not require a specific pointer gesture.
- Provide a single-pointer alternative to dragging unless dragging is essential.
- Keep focused elements at least partially visible and unobscured by sticky headers,
  cookie notices, drawers, virtual keyboards, and other author-created content.
- Use a visible focus indicator in every appearance. Do not rely on a subtle color
  shift or browser behavior that disappears against a custom surface.
- Keep help and support mechanisms in a consistent relative order across a set of
  related pages.
- Do not restrict viewport orientation unless a particular orientation is essential to
  the activity.
- Preserve pointer cancellation: initiate feedback on press, commit on release, and
  allow cancellation where the action is not inherently completed on press.

## Forms and input assistance

### Field semantics

- Use a persistent label, helpful description, native input type, and the appropriate
  `autocomplete` token for fields that collect a known user purpose.
- Use `inputmode` to request a useful keyboard, such as `email`, `tel`, `url`,
  `decimal`, or `numeric`. It does not replace validation, an accessible label, or the
  correct input type.
- Common identity tokens include `name`, `given-name`, `family-name`, `organization`,
  `email`, `tel`, `username`, `current-password`, `new-password`, and `one-time-code`.
- Never disable paste, autofill, password managers, browser-generated passwords, or
  operating-system authentication mechanisms.

### Repeated information

Information entered earlier in the same process must be auto-populated or available
for selection. Re-entry is acceptable only when it is essential, required for content
security, or the previous value is no longer valid. Browser autocomplete alone does not
satisfy this requirement.

### Errors and consequential actions

- Identify invalid fields in text, explain how to correct them, and preserve all valid
  input after failure.
- Provide suggestions when the system can determine a safe correction.
- Before a submission creates a legal or financial commitment, changes or deletes
  user-controlled data, or submits a test response, provide at least one of: reversal,
  a checked review step, or explicit confirmation with an opportunity to correct.
- Do not expire a form and discard work without warning and a recovery path.

## Authentication and account recovery

Authentication must meet WCAG 2.2 SC 3.3.8 across login, multi-factor authentication,
account recovery, reauthentication, and risk-triggered challenges.

### Password and passkey paths

- Permit password managers and browser autofill with `autocomplete="username"` and
  `autocomplete="current-password"`.
- Permit paste into usernames, passwords, recovery codes, and one-time-code fields.
- Provide a named show/hide password control that preserves focus and selection.
- Prefer WebAuthn/passkeys, operating-system authentication, or OAuth as an available
  low-cognitive-load path where they fit the product's threat model.
- Do not require users to recall selected password characters, solve a puzzle, or
  transcribe content without an assisted or non-cognitive alternative.

### One-time codes

- Mark the field with `autocomplete="one-time-code"` and a suitable input mode.
- Accept the complete code from one paste action, even when the visual design uses
  separate character boxes.
- Expose one coherent accessible name, error, and value rather than forcing a screen
  reader through unrelated single-character controls.
- Offer a non-transcription method when practical, such as a passkey, hardware key,
  approval notification, or scannable code.

### CAPTCHA and abuse controls

- Prefer rate limits, risk scoring, honeypots, proof of work, or authenticated device
  signals that do not add a cognitive task for a legitimate user.
- A text, audio-transcription, calculation, or logic CAPTCHA is not the only path
  through authentication.
- If a challenge appears only after errors, automation detection, or unusual traffic,
  it remains part of the conformance scope.
- Provide an accessible alternative and a reachable support path when automated abuse
  controls block a legitimate user.

### Recovery and lockout

- Give recovery steps clear names, status, expiration information, and error recovery.
- Preserve the original task after reauthentication whenever security permits.
- Never expose whether an unrelated person's account exists through accessibility
  messaging.
- Announce lockout and retry state without relying on color or a disappearing toast.

## Timing and session expiry

- Avoid user-facing time limits when they are not necessary.
- For a non-essential time limit, let the user turn it off, adjust it to at least ten
  times the default, or extend it after an accessible warning that allows at least 20
  seconds to act. Permit repeated extension where WCAG requires it.
- Warn before authentication or session expiry, move focus only when necessary, expose
  the remaining consequence in text, and provide an accessible extend-session action.
- Preserve entered data and restore the task after reauthentication whenever possible.
- Do not use a vanishing toast as the only expiry warning.
- Document essential real-time exceptions and test that the timing is genuinely part
  of the activity rather than a convenience for the implementation.

## Moving and live information

- Automatically moving, blinking, or scrolling content that lasts more than five
  seconds and appears beside other content needs a pause, stop, or hide control unless
  the movement is essential.
- Automatically updating information needs pause, stop, hide, or update-frequency
  control whenever it appears beside other content, unless updating is essential.
- Place the control before or adjacent to the content, give it a stable accessible name,
  and keep it keyboard operable.
- For a paused live stream, state whether resume continues from the paused position or
  jumps to the current live state.
- Do not flood a live region with every tick, waveform sample, transcript token, price,
  or telemetry update. Announce meaningful summaries and user-requested detail.
- Provide a static state for reduced motion without removing live status or control.
- Give auto-advancing carousels and rotating messages an immediately discoverable stop
  control; prefer no automatic advancement.

## Audio, video, flashes, and orientation

- Do not autoplay audible media. If audio unexpectedly runs for more than three
  seconds, provide pause/stop or independent volume control near the beginning of the
  page; the family policy is stricter and avoids this state entirely.
- User-initiated audio and video expose pause, stop, seek, mute, volume, and current
  state with keyboard and screen-reader operability as appropriate.
- Provide captions for prerecorded and live synchronized media at Level AA. Provide
  transcripts for speech-heavy content and audio descriptions where visual information
  is not otherwise available.
- Provide a text alternative for live audio-only content where required by the product
  task and disclose unavoidable latency.
- Prohibit content that flashes more than three times in any one-second period. Use a
  flash-analysis tool for borderline video, animation, game, or generated content.
- Avoid abrupt large-area luminance changes even when they remain below the formal
  flash threshold.
- Support portrait and landscape. Restrict orientation only when it is essential, such
  as a measurement whose physical orientation is intrinsic to the task.

## Public accountability

Every production product publishes a localized accessibility statement linked
consistently from the footer or support area. Start from
[accessibility-statement.md](../templates/accessibility-statement.md).

The statement includes:

- The WCAG version and target level.
- An honest conformance status, not an aspirational claim.
- The latest assessment date and method.
- Tested browser and assistive-technology combinations.
- Known limitations, affected workflows, available alternatives, and remediation
  status.
- A monitored accessible feedback channel and expected response time.
- An escalation path when the first response does not resolve the barrier.

Update the statement after a material accessibility change and review it at least once
per year. Accessibility reports contain no sensitive customer or diagnostic data.

## Normative and implementation references

- [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
- [WCAG 2.2 Understanding Documents](https://www.w3.org/WAI/WCAG22/Understanding/)
- [Accessible Authentication (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html)
- [Redundant Entry](https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html)
- [Timing Adjustable](https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html)
- [Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)
- [Developing an Accessibility Statement](https://www.w3.org/WAI/planning/statements/)

The W3C Understanding documents explain intent and techniques; the WCAG Recommendation
contains the normative conformance requirements.
