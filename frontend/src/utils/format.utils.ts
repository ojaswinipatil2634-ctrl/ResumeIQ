export const formatDate = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
};

export const formatDateShort = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

export const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const truncate = (str: string, max: number): string =>
  str.length > max ? str.slice(0, max) + '…' : str;

export const prettifyKey = (key: string): string =>
  key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

export const getInitials = (name: string | null | undefined, email: string): string => {
  if (name) {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    return parts[0].slice(0, 2).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
};

export const getFirstName = (name: string | null | undefined, email: string): string => {
  if (name) return name.trim().split(' ')[0];
  return email.split('@')[0];
};

export const getGreeting = (): string => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 18) return 'Good afternoon';
  return 'Good evening';
};

export const capitalize = (str: string): string =>
  str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

export const titleCase = (str: string): string =>
  str.split(' ').map(capitalize).join(' ');
