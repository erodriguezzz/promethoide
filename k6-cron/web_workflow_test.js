import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';
import { parseHTML } from 'k6/html';


const successCounter = new Counter('successful_requests');
const failureCounter = new Counter('failed_requests');

const test = {
  dni: '1234567890',
  flight_number: 'AA123',
  name: 'pepe', 
  lodging: 'hilton', 
  declared_money: 1000,
  smoke: true
}

export default function () {
  let res = http.get('http://apache:80/index.html');
  let success = check(res, { 'status was 200': (r) => r.status == 200 });
  success ? successCounter.add(1) : failureCounter.add(1);

  sleep(1);

  res = http.get('http://apache:80/dni.html');
  success = check(res, { 'status was 200': (r) => r.status == 200 });
  success ? successCounter.add(1) : failureCounter.add(1);

  res = res.submitForm({ 
    formSelector: 'form',
    fields: { dni: test.dni },
  });

  res = http.get(`http://apache:80/api/dni/${test.dni}`);
  success = check(res, { 'status was 404': (r) => r.status == 404 });
  success ? successCounter.add(1) : failureCounter.add(1);

  
  sleep(1);

  res = http.get('http://apache:80/load-data.html');
  success = check(res, { 'status was 200': (r) => r.status == 200 });
  success ? successCounter.add(1) : failureCounter.add(1);

  res = res.submitForm({ 
    formSelector: 'form',
   fields: { flight_number: test.flight_number },
  });

  res = http.get(`http://apache:80/api/flights/${test.flight_number}`);
  success = check(res, { 'status was 200': (r) => r.status == 200 });
  success ? successCounter.add(1) : failureCounter.add(1);
  
  sleep(1);

  res = http.get(`http://apache:80/load-viajero.html?dni=${test.dni}&flight-number=${test.flight_number}`);
  success = check(res, { 'status was 200': (r) => r.status == 200 });
  success ? successCounter.add(1) : failureCounter.add(1);

  res = res.submitForm({ 
    formSelector: 'form',
    fields: {name: test.name, lodging: test.lodging, declared_money: test.declared_money},
  });

  res = http.post('http://apache:80/api/immigration', 
    JSON.stringify(test), 
    { headers: { 'Content-Type': 'application/json' }, }
  );
  success = check(res, { 'status was 201': (r) => r.status == 201 });
  success ? successCounter.add(1) : failureCounter.add(1);

  sleep(1);

  res = http.get('http://apache:80/success.html');
  success = check(res, { 'status was 200': (r) => r.status == 200 });
  success ? successCounter.add(1) : failureCounter.add(1);
}

export function handleSummary(data) {
  const successCount = data.metrics.successful_requests ? data.metrics.successful_requests.values.count : 0;
  const failureCount = data.metrics.failed_requests ? data.metrics.failed_requests.values.count : 0;

  const result = `
  # TYPE successful_requests counter
  k6_successful_requests ${successCount}
  # TYPE failed_requests counter
  k6_failed_requests ${failureCount}
  `;

  const url = `${__ENV.PROMETHEUS_PUSHGATEWAY_URL}/metrics/job/k6_job`;
  const headers = { 'Content-Type': 'text/plain' };

  let res = http.put(url, result, { headers: headers });
  if (res.status !== 200 && res.status !== 202) {
      console.error(`Failed to push metrics to Pushgateway: ${res.status} ${res.body}`);
  } else {
      console.log(`Successfully pushed metrics to Pushgateway: ${res.status}`);
  }

  // res = http.post(url, result, { headers: headers });
  // if (res.status !== 200 && res.status !== 202) {
  //     console.error(`Failed to push metrics to Pushgateway: ${res.status} ${res.body}`);
  // } else {
  //     console.log(`Successfully pushed metrics to Pushgateway: ${res.status}`);
  // }

  return {
      'summary.json': JSON.stringify(data),
      'stdout': result
  };
}
