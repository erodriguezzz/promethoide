function nextStep(url) {
    window.location.href = url;
}

function getDniFromUrl() {
    var urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('dni');
}

function nextStep(path, dni) {
    var encodedDni = encodeURIComponent(dni);
    window.location.href = `${path}?dni=${encodedDni}`;
}

function nextStepDniFlight(path, dni, flightNumber) {
    var encodedDni = encodeURIComponent(dni);
    var encodedFlightNumber = encodeURIComponent(flightNumber);
    window.location.href = `${path}?dni=${encodedDni}&flight-number=${encodedFlightNumber}`;
}

document.getElementById('interpolForm')?.addEventListener('submit', async function (event) {
    event.preventDefault();
    const dni = document.getElementById('dni').value;
    try {
        const dniResponse = await fetch(`/api/dni/${dni}`);
        if (dniResponse.status === 200) {
            document.getElementById('interpolMessage').innerText = '❌ DNI found in interpol database. Entry cannot be created.';
        } else {
            document.getElementById('interpolMessage').innerText = '✅ DNI not found, proceed to next step.';
            // nextStep(`/load-data`);
            // nextStep(`load-flight`, dni);
            // set visible the button id="next-step-load-data"
            document.getElementById('next-step-load-data').style.display = 'block';
            // hide the form
            document.getElementById('interpolForm').style.display = 'none';
        }
    } catch (error) {
        document.getElementById('interpolMessage').innerText = `Error: ${error.message}`;
    }
});

document.getElementById('flightForm')?.addEventListener('submit', async function (event) {
    event.preventDefault();
    const flightNumber = document.getElementById('flight_number').value;
    try {
        const flightResponse = await fetch(`/api/flights/${flightNumber}`);
        if (flightResponse.status === 200) {
            document.getElementById('flightMessage').innerText = '✅ Flight found, proceed to next step.';
            // nextStep(`load-viajero`);
            // set visible the button id="next-step-load-viajero"
            document.getElementById('next-step-load-viajero').style.display = 'block';
            // hide the form
            document.getElementById('flightForm').style.display = 'none';
        } else {
            document.getElementById('flightMessage').innerText = '❌ Flight not found.';
        }
    } catch (error) {
        document.getElementById('flightMessage').innerText = `Error: ${error.message}`;
    }
});

document.getElementById('travelerForm')?.addEventListener('submit', async function (event) {
    event.preventDefault();
    const lodging = document.getElementById('lodging').value;
    const declaredMoney = document.getElementById('declared_money').value;
    const name = document.getElementById('name').value;
    const flightNumber = new URLSearchParams(window.location.search).get('flight-number');
    const dni = new URLSearchParams(window.location.search).get('dni');

    try {
        const entryResponse = await fetch('/api/immigration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                dni: dni,
                lodging: lodging,
                declared_money: declaredMoney,
                flight_number: flightNumber
            })
        });

        if (entryResponse.status === 201) {
            document.getElementById('travelerMessage').innerText = '✅ Entry created successfully.';
            // show the button id="next-step-success"
            document.getElementById('next-step-success').style.display = 'block';
            // hide the form
            document.getElementById('travelerForm').style.display = 'none';
        } else {
            const errorMessage = await entryResponse.json();
            document.getElementById('travelerMessage').innerText = `Error: ${errorMessage.detail}`;
        }
    } catch (error) {
        document.getElementById('travelerMessage').innerText = `Error: ${error.message}`;
    }
});
