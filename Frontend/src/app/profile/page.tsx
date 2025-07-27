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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRouter } from "next/navigation";
import { useToast } from "@/hooks/use-toast";
import { useState, useEffect } from "react";
import { LogOut, User } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import Link from "next/link";
import { Logo } from "@/components/logo";

const profileSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  gender: z.string().nonempty("Please select a gender."),
  state: z.string().min(2, "State is required."),
  city: z.string().min(2, "City is required."),
  age: z.coerce.number().min(1, "Age must be a positive number."),
  phoneNumber: z.string(),
  language: z.string().nonempty("Please select a language."),
});

export default function ProfilePage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: "",
      phoneNumber: "",
      gender: "",
      state: "",
      city: "",
      age: "" as any,
      language: "",
    },
  });

  useEffect(() => {
    const storedToken = localStorage.getItem("authToken");
    if (!storedToken) {
      toast({ variant: "destructive", title: "Error", description: "Token not found" });
      return;
    }

    setToken(storedToken);

    const fetchProfile = async () => {
      try {
        const storedPhone = localStorage.getItem("userPhoneNumber");
        const res = await fetch(
          `https://gah-backend-2-675840910180.europe-west1.run.app/api/farmer/profile?phone=${storedPhone}`
        );

        const data = await res.json();
        
        
        if (data.user) {
          const { name, phone, gender, state, city, age, language } = data.user;
          
          // Store phone in localStorage
          localStorage.setItem("userPhoneNumber", phone);
          form.reset({
            name,
            phoneNumber: phone,
            gender,
            state,
            city,
            age,
            language: language || "",

          });
        }
      } catch (err) {
        console.error("Failed to fetch profile:", err);
      }
    };

    fetchProfile();
  }, [form, toast]);

  async function onSubmit(values: z.infer<typeof profileSchema>) {
    setIsLoading(true);

    try {
      const res = await fetch("https:///gah-backend-2-675840910180.europe-west1.run.app/api/farmer/update_profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: values.name,
          phone: values.phoneNumber,
          password: "password", // This is hardcoded as per your instruction
          gender: values.gender,
          state: values.state,
          city: values.city,
          age: values.age,
          language: values.language,
        }),
      });

      const result = await res.json();

      toast({
        title: "Success",
        description: result.message || "Profile updated successfully",
      });

      // Optionally reset form with updated data
      if (result.user) {
        const { name, phone, gender, state, city, age, language } = result.user;
        form.reset({
          name,
          phoneNumber: phone,
          gender,
          state,
          city,
          age,
          language: language || "",
        });
      }
    } catch (error) {
      console.error("Update error:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to update profile",
      });
    } finally {
      setIsLoading(false);
    }
  }

  const handleSignOut = () => {
    localStorage.removeItem("authToken");
    toast({ title: "Signed Out", description: "You have been signed out." });
    router.push("/");
  };

  return (
    <div className="flex flex-col h-screen bg-secondary">
      <header className="flex items-center justify-between p-4 bg-background border-b shadow-sm">
        <Link href="/chat"><Logo /></Link>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/chat")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="lucide lucide-message-circle" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>
            <span className="sr-only">Chat</span>
          </Button>
          <Button onClick={handleSignOut} variant="destructive">
            <LogOut className="mr-2 h-4 w-4" /> Sign Out
          </Button>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center p-4">
        <Card className="w-full max-w-2xl shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16 border">
                <AvatarFallback><User className="h-8 w-8 text-primary" /></AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-2xl">User Profile</CardTitle>
                <CardDescription>View and update your details below.</CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField name="name" control={form.control} render={({ field }) => (
                    <FormItem>
                      <FormLabel>Full Name</FormLabel>
                      <FormControl><Input {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField name="language" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Preferred Language</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger><SelectValue placeholder="Select a language" /></SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="English">English</SelectItem>
                        <SelectItem value="Hindi">Hindi</SelectItem>
                        <SelectItem value="Marathi">Marathi</SelectItem>
                        <SelectItem value="Telugu">Telugu</SelectItem>
                        <SelectItem value="Bengali">Bengali</SelectItem>
                        {/* Add more as needed */}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )} />

                </div>

                <FormField name="phoneNumber" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone Number</FormLabel>
                    <FormControl><Input {...field} disabled /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <FormField name="gender" control={form.control} render={({ field }) => (
                    <FormItem>
                      <FormLabel>Gender</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="Male">Male</SelectItem>
                          <SelectItem value="Female">Female</SelectItem>
                          <SelectItem value="Other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />

                  <FormField name="age" control={form.control} render={({ field }) => (
                    <FormItem>
                      <FormLabel>Age</FormLabel>
                      <FormControl><Input type="number" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField name="state" control={form.control} render={({ field }) => (
                    <FormItem>
                      <FormLabel>State</FormLabel>
                      <FormControl><Input {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  
                  <FormField name="city" control={form.control} render={({ field }) => (
                  <FormItem>
                    <FormLabel>City</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />

              </div>

              <div className="flex justify-end pt-4">
                <Button
                  type="submit"
                  className="bg-accent hover:bg-accent/90"
                  disabled={isLoading}
                >
                  {isLoading ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </main>
  </div>
);
}