import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';

Vue.use( Vuex );

export const actions = {
	/**
	 * Get information about the user's favorite tools.
	 *
	 * @param {Object} context - Vuex context
	 * @param {number} page - page number
	 * @return {Promise}
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
				const data = getFailurePayload( failure );
				for ( const err in data.errors ) {
					this._vm.$notify.error(
						i18n.t( 'apierrors', [
							data.errors[ err ].field,
							data.errors[ err ].message
						] )
					);
				}
			}
		);
	},
	/**
	 * Add a tool to users favorite list of tools.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} toolname - name of the tool number
	 * @return {Promise}
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
				const data = getFailurePayload( failure );

				for ( const err in data.errors ) {
					this._vm.$notify.error(
						i18n.t( 'apierrors', [
							data.errors[ err ].field,
							data.errors[ err ].message
						] )
					);
				}
			}
		);
	},
	/**
	 * Remove a tool from the users favorite list of tools.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} toolname - name of the tool number
	 * @return {Promise}
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
				const data = getFailurePayload( failure );

				for ( const err in data.errors ) {
					this._vm.$notify.error(
						i18n.t( 'apierrors', [
							data.errors[ err ].field,
							data.errors[ err ].message
						] )
					);
				}
			}
		);
	},
	/**
	 * Check to see if a tool has been favorited.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} toolname - name of the tool number
	 * @return {Promise}
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
				const data = getFailurePayload( failure );

				if ( failure.statusCode === 404 ) {
					return false;
				}

				for ( const err in data.errors ) {
					this._vm.$notify.error(
						i18n.t( 'apierrors', [
							data.errors[ err ].field,
							data.errors[ err ].message
						] )
					);
				}
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
