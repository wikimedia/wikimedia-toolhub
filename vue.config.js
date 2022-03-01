'use strict';
const fs = require( 'fs' );
const path = require( 'path' );
const BundleTracker = require( 'webpack-bundle-tracker' );

const isProduction = process.env.NODE_ENV === 'production';
const isTest = process.env.NODE_ENV === 'test';
const PORT = process.env.PORT || 8001;

const pages = {
	main: {
		entry: path.resolve( __dirname, 'vue/src/main.js' ),
		chunks: [
			'chunk-vendors'
		]
	}
};

// Keep bundles built for running test separate from bundles for the dev/prod
// server. Test bundles skip building some things and do not split into the
// same chunks as dev/prod bundles. Why? Good question. Webpack gets angry is
// the best answer I have at the moment. :/
const buildDir = isTest ? 'vue/dist-tests' : 'vue/dist';

// T280069: Export the current git hash as an env var
process.env.VUE_APP_VERSION = require( './package.json' ).version;
process.env.VUE_APP_GIT_HASH = ( function () {
	try {
		const HEAD = fs.readFileSync(
			path.resolve( __dirname, '.git/HEAD' ), 'utf8'
		);
		if ( HEAD.indexOf( ':' ) !== -1 ) {
			// HEAD is a branch pointer, not a direct hash
			const branch = HEAD.split( ': ' )[ 1 ].trim();
			return fs.readFileSync(
				path.resolve( __dirname, '.git/' + branch ), 'utf8'
			).slice( 0, 6 );
		} else {
			return HEAD.slice( 0, 6 );
		}
	} catch ( e ) {
		// eslint-disable-next-line no-console
		console.log( 'Failed to read git hash from .git:', e );
		return 'unknown';
	}
}() );

module.exports = {
	pages: pages,
	filenameHashing: false,
	productionSourceMap: false,
	publicPath: isProduction ? '/static/' : `http://localhost:${PORT}/`,
	outputDir: path.resolve( __dirname, buildDir ),
	transpileDependencies: [
		'vuetify'
	],
	configureWebpack: {
		resolve: {
			alias: {
				'@': path.resolve( __dirname, 'vue/src' )
			},
			fallback: {
				// Empty 'stream' polyfill that would be used by
				// swagger-client to handle file uploads.
				// https://gist.github.com/ef4/d2cf5672a93cf241fd47c020b9b3066a
				stream: false
			}
		},
		// Prevent webpack from puting `eval`s into generated files
		devtool: isProduction ? false : 'cheap-source-map'
	},
	chainWebpack: ( config ) => {
		if ( !isTest ) {
			// Separate vendored js into its own bundle
			config.optimization.splitChunks(
				{
					cacheGroups: {
						vendor: {
							test: /[\\/]node_modules[\\/]/,
							name: 'chunk-vendors',
							chunks: 'all',
							priority: 1,
							enforce: true
						}
					}
				}
			);
		}

		// We are not serving pages directly, so remove plugins that generate
		// stubs for pages and including js/css.
		Object.keys( pages ).forEach( ( page ) => {
			config.plugins.delete( `html-${page}` );
			config.plugins.delete( `preload-${page}` );
			config.plugins.delete( `prefetch-${page}` );
		} );

		// Generate an index for webpack generated files that will be consumed
		// by Django's webpack_loader library.
		config.plugin( 'BundleTracker' ).use(
			BundleTracker, [ {
				filename: buildDir + '/webpack-stats.json'
			} ]
		);

		// Share a static directory between Vue and Django.
		// Use "~__STATIC__/..." from Vue code.
		config.resolve.alias.set( '__STATIC__', 'static' );

		// Copy static assets into the shared static directory.
		// https://stackoverflow.com/questions/50898675
		config.plugin( 'copy' )
			.use( require( 'copy-webpack-plugin' ) )
			.tap( ( [ pathConfigs ] ) => {
				const conf = {
					patterns: [
						{
							from: path.resolve( __dirname, 'vue/public' ),
							to: path.resolve( __dirname, 'vue/static/vue' )
						}
					]
				};
				if ( !pathConfigs ) {
					pathConfigs = conf;
				} else {
					pathConfigs.concat( conf );
				}
				return [ pathConfigs ];
			} );
	},
	devServer: {
		headers: {
			'Access-Control-Allow-Origin': [ '*' ]
		},
		host: '0.0.0.0',
		hot: 'only',
		https: false,
		port: PORT,
		static: {
			directory: path.resolve( __dirname, 'vue/public' ),
			watch: {
				poll: 1000
			}
		}
	},
	lintOnSave: false
};
