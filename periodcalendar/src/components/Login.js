import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [alertMessage, setAlertMessage] = useState(null);
  const [alertType, setAlertType] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
      
      const response = await fetch(`${process.env.REACT_APP_PERIOD_CALENDAR}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            password: password,
        }),
    });

    const responseData = await response.json();
    console.log(responseData);
    if (response.status === 200) {
        setAlertMessage('Login successful! Redirecting to the calendar page...');
      setAlertType('success');
      localStorage.setItem('userEmail', email);
      navigate('/calendar');
    } else {
        
      setAlertMessage('Login failed. Please check your email and password.');
      setAlertType('danger');
    }
    
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <h1 className="text-center mb-4">Login Page</h1>

          {alertMessage && (
            <div className={`alert alert-${alertType}`} role="alert">
              {alertMessage}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="email">Email:</label>
              <input type="email" className="form-control" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password:</label>
              <input type="password" className="form-control" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary my-4">Login</button>
          </form>
          <p className="mt-3 text-center">Don't have an account? <Link to="/register">Register here</Link>.</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
