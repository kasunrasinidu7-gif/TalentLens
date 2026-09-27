export function InitialsAvatar({ name, large = false }: { name: string; large?: boolean }) {
  const initials = name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'PL';
  return <div className={`initials-avatar${large ? ' initials-avatar-large' : ''}`} aria-label={`${name} initials`}>{initials}</div>;
}
