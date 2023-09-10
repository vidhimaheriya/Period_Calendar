import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [alertMessage, setAlertMessage] = useState(null); 
    const [alertType, setAlertType] = useState(null);
    const navigate = useNavigate();

    const handleRegistration = async (e) => {
        e.preventDefault();
        try {
            
            const response = await fetch(`${process.env.REACT_APP_PERIOD_CALENDAR}/register`, {
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
                
                setAlertMessage('Registration successful! You can login now.');
                setAlertType('success');
            } else {
                
                setAlertMessage(`Registration failed: ${responseData.error}`);
                setAlertType('danger');
            }
        } catch (error) {
            
            setAlertMessage('Error during registration. Please try again later.');
            setAlertType('danger');
        }
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <h1 className="text-center mb-4">Registration</h1>
                    
                    {alertMessage && (
                        <div className={`alert alert-${alertType}`} role="alert">
                            {alertMessage}
                        </div>
                    )}
                    <form onSubmit={handleRegistration}>
                        <div className="form-group">
                            <label htmlFor="email">Email:</label>
                            <input type="email" className="form-control" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">Password:</label>
                            <input type="password" className="form-control" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                        </div>
                        <button type="submit" className="btn btn-primary my-4">Register</button>
                    </form>
                    <p className="mt-3 text-center">Already registered? <Link to="/login">Login here</Link>.</p>
                </div>
            </div>
        </div>
    );
}

export default Register;
