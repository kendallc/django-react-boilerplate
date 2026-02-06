import * as Sentry from '@sentry/react';
import cookie from 'cookie';

import * as ApiModule from './api';
import Home from './pages/Home';

type OpenApiClient = {
  CREDENTIALS?: RequestCredentials;
  WITH_CREDENTIALS?: boolean;
  interceptors?: {
    request?: {
      use?: (fn: (request: { headers?: unknown }) => unknown) => number;
    };
  };
};

type GeneratedClient = {
  setConfig?: (config: { credentials?: RequestCredentials }) => void;
  interceptors?: {
    request?: {
      use?: (fn: (request: Request) => Request) => number;
    };
  };
};

const withCsrfHeaders = (existingHeaders?: Headers | Record<string, string>) => {
  const headers = new Headers(existingHeaders);
  const { csrftoken } = cookie.parse(document.cookie);

  if (csrftoken) {
    headers.set('X-CSRFTOKEN', csrftoken);
  }

  return headers;
};

const api = ApiModule as unknown as {
  OpenAPI?: OpenApiClient;
  client?: GeneratedClient;
};

if (api.OpenAPI) {
  api.OpenAPI.CREDENTIALS = 'include';
  api.OpenAPI.WITH_CREDENTIALS = true;
  api.OpenAPI.interceptors?.request?.use?.((request) => ({
    ...request,
    headers: withCsrfHeaders(request.headers as Headers | Record<string, string> | undefined),
  }));
}

if (api.client) {
  api.client.setConfig?.({ credentials: 'include' });
  api.client.interceptors?.request?.use?.((request) => {
    const headers = withCsrfHeaders(request.headers);
    return new Request(request, { headers });
  });
}

const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <Home />
  </Sentry.ErrorBoundary>
);

export default App;
