import React from "react";
import { Toaster } from "@/components/ui/toaster";
import Home from "./Home";
import { Route, Routes } from "react-router-dom";
import AddDocument from "./AddDocument";

const App = () => {
    return (
        <>
            <Toaster />
            <Routes>
                <Route exact path="/" element={<Home />} />
                <Route exact path="/add-doc" element={<AddDocument />} />
            </Routes>
        </>
    );
};

export default App;
