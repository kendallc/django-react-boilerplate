import * as Sentry from '@sentry/react';
import cookie from 'cookie';

import { client } from './api/client.gen';
import Home from './pages/Home';

client.setConfig({
  credentials: 'include',
});

client.interceptors.request.use((request) => {
  const { csrftoken } = cookie.parse(document.cookie);
  if (!csrftoken) {
    return request;
  }

  const headers = new Headers(request.headers);
  headers.set('X-CSRFTOKEN', csrftoken);
  return new Request(request, { headers });
});

const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <Home />
  </Sentry.ErrorBoundary>
);

export default App;
