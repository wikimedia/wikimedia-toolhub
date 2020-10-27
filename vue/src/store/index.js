import Vue from 'vue';
import Vuex from 'vuex';

Vue.use( Vuex );

export default new Vuex.Store( {
	state: {
		user: {
			is_authenticated: false
		},
		toolFiles: []
	},
	getters: {
		allToolFiles: ( state ) => state.toolFiles
	},
	mutations: {
		USER( state, user ) {
			state.user = user;
		},
		ADD_TOOL_FILE( state, file ) {
			state.toolFiles.unshift( file );
		},
		REMOVE_TOOL_FILE( state, file ) {
			const index = state.toolFiles.findIndex( ( toolFile ) => toolFile === file );
			state.toolFiles.splice( index, 1 );
		}
	},
	actions: {
		getUserInfo( context ) {
			console.log( 'store.index.actions.getUserInfo() called' );
			fetch( '/user/info/', { credentials: 'same-origin' } )
				.then( ( response ) => response.json() )
				.then( ( data ) => ( context.commit( 'USER', data.user ) ) );
		},
		addToolFile( context, file ) {
			context.commit( 'ADD_TOOL_FILE', file );
		},
		removeToolFile( context, file ) {
			context.commit( 'REMOVE_TOOL_FILE', file );
		}
	},
	modules: {
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
} );
