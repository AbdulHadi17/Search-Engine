"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import { Moon, Sun } from "lucide-react";

export default function AddDocument() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        company_name: "",
        description: "",
        title: "",
        location: "",
        skills_desc: "",
    });

    const [isDarkMode, setIsDarkMode] = useState(true);

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
    }, [isDarkMode]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (Object.values(formData).some((value) => value.trim() === "")) {
            toast({
                title: "Error",
                description:
                    "All fields are mandatory. Please fill in all the fields.",
                variant: "destructive",
            });
            return;
        }

        const csv = Object.values(formData)
            .map((value) => `"${value.replace(/"/g, '""')}"`)
            .join(",");

        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });

        const link = document.createElement("a");
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", "document_data.csv");
            link.style.visibility = "hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        toast({
            title: "Success",
            description: "Document added successfully. CSV file downloaded.",
        });

        setFormData({
            company_name: "",
            description: "",
            title: "",
            location: "",
            skills_desc: "",
        });
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-900 dark:to-blue-900 transition-colors duration-500">
            <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-700 [mask-image:linear-gradient(to_bottom,white,transparent)] pointer-events-none"></div>
            <main className="relative flex min-h-screen flex-col items-center justify-start p-24">
                <Button
                    variant="outline"
                    size="icon"
                    className="absolute top-4 right-4"
                    onClick={() => setIsDarkMode(!isDarkMode)}
                >
                    {isDarkMode ? (
                        <Sun className="h-[1.2rem] w-[1.2rem]" />
                    ) : (
                        <Moon className="h-[1.2rem] w-[1.2rem]" />
                    )}
                </Button>

                <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
                    Add New Document
                </h1>
                <form
                    onSubmit={handleSubmit}
                    className="w-full max-w-2xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-6 rounded-lg shadow-md space-y-6"
                >
                    <div>
                        <Label
                            htmlFor="company_name"
                            className="text-gray-800 dark:text-gray-300"
                        >
                            Company Name
                        </Label>
                        <Input
                            id="company_name"
                            name="company_name"
                            value={formData.company_name}
                            onChange={handleChange}
                            placeholder="Enter company name"
                            className="mt-2"
                            required
                        />
                    </div>
                    <div>
                        <Label
                            htmlFor="description"
                            className="text-gray-800 dark:text-gray-300"
                        >
                            Description
                        </Label>
                        <Textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            placeholder="Enter company description"
                            className="mt-2"
                            required
                        />
                    </div>
                    <div>
                        <Label
                            htmlFor="title"
                            className="text-gray-800 dark:text-gray-300"
                        >
                            Title
                        </Label>
                        <Input
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            placeholder="Enter job title"
                            className="mt-2"
                            required
                        />
                    </div>
                    <div>
                        <Label
                            htmlFor="location"
                            className="text-gray-800 dark:text-gray-300"
                        >
                            Location
                        </Label>
                        <Input
                            id="location"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            placeholder="Enter job location"
                            className="mt-2"
                            required
                        />
                    </div>
                    <div>
                        <Label
                            htmlFor="skills_desc"
                            className="text-gray-800 dark:text-gray-300"
                        >
                            Skills Description
                        </Label>
                        <Input
                            id="skills_desc"
                            name="skills_desc"
                            value={formData.skills_desc}
                            onChange={handleChange}
                            placeholder="Enter required skills"
                            className="mt-2"
                            required
                        />
                    </div>
                    <Button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    >
                        Add Document
                    </Button>
                </form>
                <Button
                    variant="outline"
                    className="mt-4 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300"
                    onClick={() => navigate("/")}
                >
                    Back to Search
                </Button>
            </main>
        </div>
    );
}
