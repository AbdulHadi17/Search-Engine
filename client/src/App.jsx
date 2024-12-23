import React from "react";
import Home from "./Home";
import { Route, Routes } from "react-router-dom";
import AddingDoc from "./AddingDoc";
// import Results from './Results';

const App = () => {
    return (
        <>
            <Routes>
                <Route exact path="/" element={<Home />} />
                <Route exact path="/add-doc" element={<AddingDoc />} />
                {/* <Route path='/results' element={<Results/>}/> */}
            </Routes>
        </>
    );
};

export default App;
