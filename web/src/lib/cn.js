// Tiny className combiner — filters falsy values and joins with spaces.
export function cn(...classes) {
  return classes.flat().filter(Boolean).join(' ')
}
