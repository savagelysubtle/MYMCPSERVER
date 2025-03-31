import pino from 'pino';

export const logger = pino({
  name: 'typescript-tool-server',
  level: process.env.LOG_LEVEL || 'info',
  timestamp: true,
  formatters: {
    level(label) {
      return { level: label };
    },
  },
});
