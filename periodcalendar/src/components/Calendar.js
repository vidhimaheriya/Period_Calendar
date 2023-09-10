import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Form, Row, Col } from 'react-bootstrap';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import './Calendar.css';

const CalendarPage = () => {
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [cycleDays, setCycleDays] = useState('');
    const [nextPeriodDate, setNextPeriodDate] = useState('');
    const [periodStarted, setPeriodStarted] = useState(false);
    const [userEmail, setUserEmail] = useState('')
    const navigate = useNavigate();

    const fetchSavedChoices = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_PERIOD_CALENDAR}/getdata`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: localStorage.getItem('userEmail')
                }),
            });
            console.log(response);
            const responseData = await response.json();
            console.log(responseData);

            if (response.status === 200 && responseData.selectedDate && responseData.cycleDays) {
                // Returning user, show existing data and update state
                setSelectedDate(new Date(responseData.selectedDate));
                setCycleDays(responseData.cycleDays.toString());
            } else {
                // First-time user or error in fetching data, reset state or show appropriate form
                setSelectedDate(new Date());
                setCycleDays('');
                setPeriodStarted(false);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    const handleStartPeriod = async () => {
        if (selectedDate && cycleDays) {
            try {
                // Check if user is a returning user or first-time user
                if (periodStarted) {
                    // Returning user, use the /period_date API endpoint
                    const new_response = await fetch(`${process.env.REACT_APP_PERIOD_CALENDAR}/period_date`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: localStorage.getItem('userEmail'),
                            selectedDate: selectedDate.toLocaleDateString('en-US'),
                        }),
                    });
                    console.log(new_response);
                    const new_responseData = await new_response.json();
                    setCycleDays(new_responseData.cycleDays);
                    setNextPeriodDate(new_responseData.nextPeriodDate);
                    console.log(nextPeriodDate);
                    setPeriodStarted(true);
                } else {
                    // First-time user, use the /period_cycle API endpoint
                    const first_response = await fetch(`${process.env.REACT_APP_PERIOD_CALENDAR}/period_cycle`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: localStorage.getItem('userEmail'),
                            selectedDate: selectedDate.toISOString().slice(0, 10),
                            cycleDays: parseInt(cycleDays),
                        }),
                    });
                    const first_responseData = await first_response.json();
                    // setCycleDays(first_responseData.cycleDays);
                    setNextPeriodDate(first_responseData.nextPeriodDate);
                    console.log('first');
                    console.log(nextPeriodDate);
                    setPeriodStarted(true);
                }

                console.log('Start Period from Selected Date:', selectedDate);
                console.log('Cycle Days:', cycleDays);
                setPeriodStarted(true); // Set periodStarted to true after successful execution
            } catch (error) {
                console.error('Error starting period:', error);
            }
        } else {
            alert('Please select a date and fill in the cycle days.');
        }
    };

    const handleLogout = () => {
        setSelectedDate(new Date());
        setCycleDays('');
        setPeriodStarted(false);
        localStorage.removeItem('userEmail')
        navigate('/login');
    }

    // Fetch already saved choices when the component mounts
    useEffect(() => {
        setUserEmail(localStorage.getItem('userEmail'));
        fetchSavedChoices();
    }, []);

    return (
        <div>

            {/* Navigation Bar */}
            <nav className="navbar navbar-dark bg-dark">
                <span className="navbar-brand mx-4">Period Calendar</span>
                {userEmail && (
                    <div className="form-inline">
                        <span className="navbar-text">{userEmail}</span>
                        <button className="btn btn-danger mx-4" onClick={handleLogout}>Logout</button>
                    </div>
                )}
            </nav>
            <div className="calendarPage">
                <h1>Period Calendar</h1>
                {periodStarted && (
                    <div className="alert alert-success mt-4" role="alert">
                        Your next period reminder has been set !
                    </div>

                )}
                <div className="calendarContainer mx-4">
                    <Calendar
                        value={selectedDate}
                        onChange={setSelectedDate}
                    />
                    <div className="infoForm mx-4">
                        <h2>Period Information</h2>
                        <Row>
                            <Col>
                                <Form.Group controlId="cycleDays">
                                    <Form.Label>Menstrual Cycle Days:</Form.Label>
                                    <Form.Control
                                        type="number"
                                        placeholder="Enter number of cycle days"
                                        value={cycleDays}
                                        onChange={(e) => setCycleDays(e.target.value)}
                                        disabled={!selectedDate || periodStarted}
                                        required
                                    />
                                </Form.Group>
                                <Form.Group controlId="selectedDate">
                                    <Form.Label>Period Starts:</Form.Label>
                                    <Form.Control
                                        type="date"
                                        value={selectedDate.toISOString().slice(0, 10)}
                                        onChange={(e) => setSelectedDate(new Date(e.target.value))}
                                        required
                                    />
                                </Form.Group>
                                <Button variant="primary" className='my-4' onClick={handleStartPeriod}>
                                    Start Period
                                </Button>

                            </Col>
                        </Row>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CalendarPage;
