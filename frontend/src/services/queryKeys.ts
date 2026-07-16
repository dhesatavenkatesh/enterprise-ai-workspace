export const queryKeys = {
  auth: {
    all: [
      "auth",
    ] as const,

    currentUser: [
      "auth",
      "current-user",
    ] as const,
  },

  users: {
    all: [
      "users",
    ] as const,
  },

  dashboard: {
    all: [
      "dashboard",
    ] as const,

    statistics: [
      "dashboard",
      "statistics",
    ] as const,
  },
}