import { Leaf } from "lucide-react";

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <Leaf className="h-8 w-8 text-primary" />
      <h1 className="text-2xl font-bold text-primary font-headline">FarmAI</h1>
    </div>
  );
}
