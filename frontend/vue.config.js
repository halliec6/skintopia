const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: "/skintopia-test/",
  pages: {
    index: {
      entry: "src/main.ts",
      title: "Skintopia",
    },
  },
});
