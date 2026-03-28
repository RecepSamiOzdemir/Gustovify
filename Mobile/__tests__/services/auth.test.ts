jest.mock('../../services/storage', () => ({
    Storage: {
        getItem: jest.fn().mockResolvedValue(null),
        setItem: jest.fn().mockResolvedValue(undefined),
        deleteItem: jest.fn().mockResolvedValue(undefined),
    },
}));

jest.mock('../../constants/Config', () => ({
    API_URL: 'http://localhost:8000',
}));

describe('Auth Service', () => {
    it('should export authService', () => {
        const { authService } = require('../../services/auth');
        expect(authService).toBeDefined();
        expect(authService.login).toBeDefined();
        expect(authService.register).toBeDefined();
        expect(authService.logout).toBeDefined();
        expect(authService.refreshToken).toBeDefined();
    });
});
