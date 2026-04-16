# Frontend Component Reference — LoreForge

Load this file when building or modifying UI components.

## Component Conventions
- Framework: your frontend framework
- Component naming: PascalCase, one component per file
- File location: `src/components/`
- Styling approach: Tailwind CSS

## State Management
React hooks + Context API

## Standard Props Pattern
```
// Always type your props
interface ComponentNameProps {
  // required props
  // optional props with ?
}
```

## Accessibility Rules
- All interactive elements must have accessible labels
- Use semantic HTML elements (button, nav, main, etc.)
- Keyboard navigation must work for all interactive UI

## Do Not
- Create business logic inside UI components
- Make API calls directly in components — use service/hook abstractions
- Use inline styles except for truly dynamic values

---
*Evolve this document as you establish new patterns. Add examples from real code.*
