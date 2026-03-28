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

describe('API Service', () => {
    it('should export api object with CRUD methods', () => {
        const { api } = require('../../services/api');
        expect(api).toBeDefined();
        expect(api.get).toBeDefined();
        expect(api.post).toBeDefined();
        expect(api.put).toBeDefined();
        expect(api.delete).toBeDefined();
    });
});
