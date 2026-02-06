import { render, screen, waitFor } from '@testing-library/react';

import * as ApiModule from '../../api';
import Home from '../Home';

jest.mock('../../api', () => ({
  restRestCheckRetrieve: jest.fn(),
  CommonService: {
    restRestCheckRetrieve: jest.fn(),
  },
}));

const api = ApiModule as unknown as {
  restRestCheckRetrieve: jest.Mock;
};

describe('Home', () => {
  beforeEach(() => {
    api.restRestCheckRetrieve.mockResolvedValue({
      message: 'Test Result',
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders static assets and rest API data', async () => {
    render(<Home />);

    expect(screen.getByText('Static assets')).toBeInTheDocument();
    expect(screen.getByText('Rest API')).toBeInTheDocument();
    expect(await screen.findByText('Test Result')).toBeInTheDocument();
  });

  test('calls restRestCheckRetrieve on mount', async () => {
    render(<Home />);

    await waitFor(() => {
      expect(api.restRestCheckRetrieve).toHaveBeenCalledWith();
    });
  });
});
