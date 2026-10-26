# Motion and Interaction

Inherited from the Relux Works product web design system. Swarma changes are marked. The
book's diagrams carry no volume, shadow or decoration (`diagram-style:9`; notation as in
[swarma-identity.md](swarma-identity.md)), and Swarma motion follows the same restraint: it shows a
state change and stops.

## Motion tokens

Use a small timing vocabulary:

| Token | Range | Use |
| --- | --- | --- |
| Press | 80-100ms | Immediate scale or color feedback on pointer-down |
| Fast | 120-160ms | Menu items, hover, focus, compact state changes |
| Base | 200-240ms | Drawer, popover, small surface transition |
| Spatial | Spring, 300-400ms response | Interruptible direct manipulation only |

Ordinary interface motion is critically damped and does not overshoot. Add a small
bounce only when a drag or flick supplied momentum.

## Immediate feedback

- Start visual feedback on `pointerdown` or `:active`, not after `click`.
- Keep feedback continuous during a drag, resize, or scrub.
- Commit tap actions on release and allow cancellation by moving away before release.
- Keep the visible press subtle: a small scale change or state color is enough.

```css
.control:active {
  transform: scale(0.98);
  transition: transform var(--motion-press) ease-out;
}
```

## Interruptibility

The user can reverse an opening drawer, expanding menu, or dragged surface at any
moment.

- Never disable input only because a transition is running.
- Retarget from the element's current rendered value, not from the previous logical
  destination.
- Preserve velocity when a gesture hands off to a spring.
- Use a proven spring or gesture library for drawers, sheets, carousels, and physics.
  Do not hand-roll domain physics for an established interaction.
- Keep X and Y motion independent when their velocities differ.

CSS transitions are appropriate for simple menus and state fades when they can be
reversed from the current computed state. Gesture-driven surfaces need a runtime that
supports velocity and interruption.

## Spatial consistency

- Enter and exit along the same path.
- Set popover and menu origins from their trigger rather than from the viewport center.
- A logical-end drawer exits toward logical end, including in RTL.
- Keep the trigger and the resulting state spatially related.
- Do not make unrelated page sections rise, fade, or stagger merely because they
  entered the viewport.

## Menu behavior

A navigation menu is complete only when it supports:

- Pointer, keyboard, and touch activation.
- Immediate trigger feedback.
- `Escape`, outside press, and route-change closing.
- Focus moved into a modal drawer and returned to its trigger on close.
- Background scroll lock and non-interactive background content while modal.
- Stable page width while scroll is locked.
- Rapid open-close-open reversal without a jump or stale invisible overlay.
- A 120-160ms transform and opacity transition, with no bounce.
- A static or short cross-fade equivalent for reduced motion.

Use native disclosure semantics for a non-modal compact menu. Use a dialog pattern for
a modal drawer; do not mix their keyboard contracts.

## Identity artwork

- Keep the Swarma wordmark, the Swarma mark once supplied, and the Relux Works operator artwork
  static.
- Do not rotate, skew, morph, pulse, glow, draw on, or separate their elements.
- Do not repurpose the operator's chevron or northeast arrow, or any part of the future Swarma
  mark, as loading, progress, redirect, or synchronization animation.
- Apply linked-logo hover and focus feedback to its container or focus indicator; do
  not alter the artwork's geometry, spacing, or relative colors.

## Gestures

Add gestures only when they reduce effort for the product's primary workflow.

- Use Pointer Events and `setPointerCapture`.
- Preserve the offset where the element was grabbed.
- Require roughly 10px of movement before committing to a direction.
- Track recent position and time samples to calculate release velocity.
- Project momentum before selecting a snap point, then hand velocity to the spring.
- Apply progressive rubber-band resistance beyond a boundary instead of a hard stop.
- Always provide an explicit control and keyboard path equivalent to the gesture.

## Domain motion

Motion may carry product meaning:

- Playback progress and active audio state.
- Synchronization, streaming, recording, or connection status.
- Spatial topology, drag placement, or a live data transition.
- Completion, warning, error, or a confirmed state change.

Continuous animation is not a default decoration. An indicator may move while a real
operation runs and must stop when it ends. Status must also be available in text and not
depend on motion alone.

**Swarma additions:**

- Book figures, trust boundaries, role markers, status badges and the layer order never animate.
  They describe structure, and structure does not move.
- No particles, flowing connection lines, pulsing nodes or "swarm" movement anywhere. The book has
  no such imagery (see [swarma-identity.md](swarma-identity.md), "Rejected candidates").
- No scroll-triggered entrance animations for sections.

## Performance

- Animate `transform` and `opacity` for ordinary transitions.
- Reserve `will-change` for elements about to move and remove it after long-lived
  motion where possible.
- Use `requestAnimationFrame` for direct manipulation.
- Avoid layout reads and writes interleaved in every frame.
- Test on a throttled mobile device, not only a desktop development machine.
- Prevent animation and font loading from shifting fixed-format controls or media.

## User preferences

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
  }

  .spatial-transition {
    transform: none !important;
    transition: opacity 120ms linear;
  }
}

@media (prefers-reduced-transparency: reduce) {
  .material {
    background: var(--color-surface-raised);
    backdrop-filter: none;
  }
}
```

Reduced motion retains feedback through short opacity, color, and state changes. It
removes parallax, large slides, looping movement, elastic overshoot, and momentum.
Reduced transparency uses an opaque surface with equivalent hierarchy.
