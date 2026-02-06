import * as Sentry from '@sentry/react';
import type { AxiosRequestConfig } from 'axios';
import cookie from 'cookie';

import { OpenAPI } from './api';
import Home from './pages/Home';

OpenAPI.CREDENTIALS = 'include';
OpenAPI.WITH_CREDENTIALS = true;

OpenAPI.interceptors.request.use((request: AxiosRequestConfig) => {
  const { csrftoken } = cookie.parse(document.cookie);
  if (!csrftoken) {
    return request;
  }

  return {
    ...request,
    headers: {
      ...(request.headers as Record<string, string> | undefined),
      'X-CSRFTOKEN': csrftoken,
    },
  };
});

const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <Home />
  </Sentry.ErrorBoundary>
);

export default App;
