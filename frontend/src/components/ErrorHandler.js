export const handleError = (error, setError) => {
    if (error.response) {
        switch (error.response.status) {
            case 422:
                const schema_error = JSON.parse(error.request.response);
                setError('Validation Error: ' + (schema_error.detail[0]?.msg || 'Invalid input'));
                break;
            case 500:
                setError('Server Error: Please try again later');
                break;
            case 401:
                setError('Error: ' + (error.response.statusText || 'You were logged out!'));
                break;
            default:
                const default_error = JSON.parse(error.request.response);
                setError('Error: ' + (default_error.detail || 'An unexpected error occurred'));
                break;
        }
    } else if (error.request) {
        setError('Network Error: No response received from server');
    } else {
        setError('Error: ' + error.message);
    }
    console.error('Error:', error);
};
