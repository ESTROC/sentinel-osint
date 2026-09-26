import clsx from 'clsx';
import type { Priority } from '@/lib/types';

export function PriorityBadge({ priority }: { priority: Priority }) {
  return <span className={clsx('badge', `badge-${priority.toLowerCase()}`)}>{priority}</span>;
}
