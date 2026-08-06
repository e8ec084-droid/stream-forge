const BASE_URL = "http://127.0.0.1:8000/api";

async function request(path) {
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export const getWeek1Data = () => request("/week1");
export const getWeek2Data = () => request("/week2");
export const getMidReviewData = () => request("/mid-review");
