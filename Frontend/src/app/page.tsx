"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/logo";
import { useToast } from "@/hooks/use-toast"; // ✅ Import toast hook
import { useState } from "react";

// ✅ Validation schema
const formSchema = z.object({
  phoneNumber: z.string().min(10, "Phone number must be at least 10 digits."),
  password: z.string().min(6, "Password must be at least 6 characters."),
});

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast(); // ✅ Used to show notifications
  const [isLoading, setIsLoading] = useState(false); // ✅ Loading state

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      phoneNumber: "",
      password: "",
    },
  });

  // ✅ Handles form submission
  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true); // Start loader
    try {
      const response = await fetch(
        "https://gah-backend-2-675840910180.europe-west1.run.app/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            phone: values.phoneNumber,
            password: values.password,
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Login failed. Please try again.");
      }

      // ✅ Save token in localStorage
      localStorage.setItem("authToken", result.token);
      localStorage.setItem("userPhoneNumber",result.phone);

      //print token in console
      console.log(localStorage.getItem("authToken"));

      // ✅ Show success message
      toast({
        title: "Login Successful",
        description: result.message || "You have successfully logged in.",
      });

      router.push("/chat"); // ✅ Redirect to chat

    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Login Error",
        description: error.message || "An unexpected error occurred.",
      });
    } finally {
      setIsLoading(false); // Stop loader
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <Card className="w-full max-w-sm shadow-lg">
        <CardHeader className="items-center text-center">
          <Logo />
          <CardTitle className="text-2xl pt-4">Welcome Back!</CardTitle>
          <CardDescription>
            Sign in to continue to your farm dashboard.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="phoneNumber"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone Number</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter your phone number"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="Enter your password"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button
                type="submit"
                className="w-full bg-accent hover:bg-accent/90"
                disabled={isLoading}
              >
                {isLoading ? "Logging in..." : "Login"}
              </Button>
            </form>
          </Form>
        </CardContent>
        <div className="p-6 pt-0 text-center text-sm">
          <p>
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              className="font-medium text-primary hover:underline"
            >
              Register here
            </Link>
          </p>
        </div>
      </Card>
    </main>
  );
}




