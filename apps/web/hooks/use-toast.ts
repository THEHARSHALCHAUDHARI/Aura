"use client";
import { toast as sonnerToast } from "sonner";

export function useToast() {
  const toast = ({
    title,
    description,
    variant,
  }: {
    title?: string;
    description?: string;
    variant?: "default" | "destructive" | string;
  }) => {
    sonnerToast(title ?? "Notification", {
      description,
      className:
        variant === "destructive" ? "bg-red-500 text-white" : undefined,
    });
  };

  return { toast };
}
