const path = require("path")
const BundleTracker = require("webpack-bundle-tracker");

const isProduction = process.env.NODE_ENV === "production";
const PORT = process.env.PORT || 8001;

const pages = {
  "main": {
    "entry": "./vue/src/main.js",
    "chunks": [
      "chunk-vendors"
    ]
  }
};

module.exports = {
  pages: pages,
  filenameHashing: false,
  productionSourceMap: false,
  publicPath: isProduction ? "" : `http://localhost:${PORT}/`,
  // FIXME: what path should this be?
  outputDir: path.resolve(__dirname, "vue/static"),
  transpileDependencies: [
    "vuetify"
  ],
  configureWebpack: {
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "vue/src")
      }
    },
    // Prevent webpack from puting `eval`s into generated files
    devtool: "inline-source-map"
  },
  chainWebpack: config => {
    // Separate vendored js into its own bundle
    config.optimization.splitChunks(
      {
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
              name: "chunk-vendors",
              chunks: "all",
              priority: 1,
              enforce: true
            },
        },
        }
    );

    // We are not serving pages directly, so remove plugins that generate
    // stubs for pages and including js/css.
    Object.keys(pages).forEach(page => {
      config.plugins.delete(`html-${page}`);
      config.plugins.delete(`preload-${page}`);
      config.plugins.delete(`prefetch-${page}`);
    });

    // Generate an index for webpack generated files that will be consumed by
    // Django's webpack_loader library.
    // FIXME: make this track outputDir
    config.plugin("BundleTracker").use(
      BundleTracker, [{
        filename: "vue/static/vue/webpack-stats.json"
      }]
    );

    // Share a static directory between Vue and Django.
    // Use "~__STATIC__/..." from Vue code.
    config.resolve.alias.set("__STATIC__", "static");

    // Copy static assets into the shared static directory.
    // https://stackoverflow.com/questions/50898675
    config.plugin("copy")
      .use(require("copy-webpack-plugin"))
      .tap(([pathConfigs]) => {
        var conf = [{
          from: path.resolve(__dirname, "vue/public"),
          to: path.resolve(__dirname, "vue/static/vue")
        }]
        if (!pathConfigs) {
          pathConfigs = conf
        } else {
          pathConfigs.concat(conf)
        }
        return [pathConfigs]
      });

    // Configure the dev-mode http server for hot reloading
    config.devServer
      .public(`http://0.0.0.0:${PORT}`)
      .host("0.0.0.0")
      .port(PORT)
      .hotOnly(true)
      .watchOptions({poll: 1000})
      .https(false)
      .headers({"Access-Control-Allow-Origin": ["*"]});
  },
  devServer: {
    contentBase: path.join(__dirname, "vue/public")
  },
  lintOnSave: false
}