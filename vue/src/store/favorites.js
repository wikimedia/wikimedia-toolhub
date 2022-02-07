import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall } from '@/plugins/swagger';
import { displayErrorNotification } from '@/helpers/notifications';

Vue.use( Vuex );

export const actions = {
	/**
	 * Get information about the user's favorite tools.
	 *
	 * @param {Object} context - Vuex context
	 * @param {number} page - page number
	 * @return {Promise<undefined>}
	 */
	getFavoriteTools( context, page ) {
		const request = {
			url: '/api/user/favorites/?page=' + page
		};
		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'FAVORITE_TOOLS', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Add a tool to users favorite list of tools.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} toolname - name of the tool number
	 * @return {Promise<undefined>}
	 */
	addTool( context, toolname ) {
		const request = {
			url: '/api/user/favorites/',
			method: 'POST',
			body: JSON.stringify( { name: toolname } )
		};
		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'ADD_FAVORITE', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Remove a tool from the users favorite list of tools.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} toolname - name of the tool number
	 * @return {Promise<undefined>}
	 */
	removeTool( context, toolname ) {
		const request = {
			url: '/api/user/favorites/' + toolname + '/',
			method: 'DELETE'
		};
		return makeApiCall( context, request ).then(
			() => {
				context.commit( 'REMOVE_FAVORITE', toolname );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Check to see if a tool has been favorited.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} toolname - name of the tool number
	 * @return {Promise<undefined>}
	 */
	isFavorite( context, toolname ) {
		const request = {
			url: '/api/user/favorites/' + toolname + '/'
		};
		return makeApiCall( context, request ).then(
			() => {
				return true;
			},
			( failure ) => {

				if ( failure.statusCode === 404 ) {
					return false;
				}
				displayErrorNotification.call( this, failure );
				return false;
			}
		);
	}
};

export const mutations = {
	FAVORITE_TOOLS( state, favorites ) {
		state.favoriteTools = favorites.results;
		state.numFavoriteTools = favorites.count;
	},
	ADD_FAVORITE( state, tool ) {
		state.favoriteTools.push( tool );
		state.numFavoriteTools += 1;
	},
	REMOVE_FAVORITE( state, toolname ) {
		const index = state.favoriteTools.findIndex(
			( obj ) => obj.name === toolname
		);
		state.favoriteTools.splice( index, 1 );
		state.numFavoriteTools -= 1;
	}
};

export default {
	namespaced: true,
	state: {
		favoriteTools: [],
		numFavoriteTools: 0
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
