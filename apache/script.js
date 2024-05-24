document.getElementById('entryForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const dni = document.getElementById('dni').value;
    const flightNumber = document.getElementById('flight_number').value;
    const lodging = document.getElementById('lodging').value;
    const declaredMoney = document.getElementById('declared_money').value;

    try {
        const dniResponse = await fetch(`http://localhost:8080/api/dni/${dni}`);
        if (dniResponse.status === 200) {
            document.getElementById('message').innerText = 'DNI found in interpol database. Entry cannot be created.';
            return;
        }

        const flightResponse = await fetch(`http://localhost:8080/api/flights/${flightNumber}`);
        if (flightResponse.status !== 200) {
            document.getElementById('message').innerText = 'Flight not found. Entry cannot be created.';
            return;
        }

        const entryResponse = await fetch('http://localhost:8080/api/immigration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                name: 'Unknown Passenger',
                dni: dni,
                lodging: lodging,
                declared_money: declaredMoney,
                flight_number: flightNumber
            })
        });

        if (entryResponse.status === 201) {
            document.getElementById('message').innerText = 'Entry created successfully.';
        } else {
            const errorMessage = await entryResponse.json();
            document.getElementById('message').innerText = `Error: ${errorMessage.detail}`;
        }
    } catch (error) {
        document.getElementById('message').innerText = `Error: ${error.message}`;
    }
});