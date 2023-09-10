import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Calendar from './components/Calendar';

import 'bootstrap/dist/css/bootstrap.min.css';

const App =()=> {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />}></Route>
        <Route path="/register" element={<Register />}></Route>
        <Route path="/calendar" element={<Calendar />}></Route> 
        {/* Route unknown paths to registration */}
        <Route path="*" element={<Register />}></Route>
      </Routes>
    </Router>
  );
}

export default App;
