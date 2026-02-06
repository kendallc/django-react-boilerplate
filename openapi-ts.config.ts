import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './backend/schema.yml',
  output: {
    path: 'frontend/js/api',
    postProcess: ['prettier'],
  },
  client: 'axios',
  useOptions: true,
});
