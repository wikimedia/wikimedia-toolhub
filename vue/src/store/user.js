import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall } from '@/plugins/swagger';
import { displayErrorNotification } from '@/helpers/notifications';

Vue.use( Vuex );

export const actions = {
	/**
	 * Get information about the current user.
	 *
	 * @param {Object} context - Vuex context
	 * @param {Object} payload
	 * @param {Object} payload.vm - Vue
	 * @return {Promise}
	 */
	getUserInfo( context, { vm } ) {
		if ( context.state.userPromise ) {
			return context.state.userPromise;
		}
		const request = {
			url: '/api/user/'
		};
		const promise = makeApiCall( context, request ).then(
			( success ) => {
				const user = success.body;
				context.commit( 'USER', user );
				// Set the user's abilities
				vm.$ability.update( user.casl );
				return user;
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);

		context.commit( 'USER_PROMISE', promise );
		return promise;
	},
	listAllUsers( context, payload ) {
		const filters = payload.filters;
		const params = [
			[ 'page', payload.page ],
			[ 'username__contains', filters.username ],
			[ 'groups__id', filters.groups_id ]
		];

		const cleanParams = new URLSearchParams(
			params.filter( ( value ) => {
				const val = value[ 1 ];
				return val !== null && val !== undefined;
			} )
		);

		const request = { url: '/api/users/?' + cleanParams.toString() };

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'USERS', success.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	setLocale( context, locale ) {
		const request = {
			url: '/api/user/locale/',
			method: 'POST',
			mode: 'same-origin',
			body: JSON.stringify( { language: locale } )
		};

		makeApiCall( context, request ).then(
			() => {},
			( failure ) => {
				if ( failure.status === 403 ) {
					// Forbidden response from API is always a missing CSRF
					// problem. Fetch the user state and try again.
					context.dispatch( 'getUserInfo' ).then( () => {
						context.dispatch( 'setLocale', locale );
					} );
				} else {
					throw failure;
				}
			}
		);
	},
	/**
	 * Fetch the current user's current authtoken.
	 *
	 * @param {Object} context - Vuex context
	 * @return {Promise}
	 */
	getAuthtoken( context ) {
		const request = {
			url: '/api/user/authtoken/'
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'AUTHTOKEN', success.body.token );
			},
			( failure ) => {
				if ( failure.statusCode === 404 ) {
					context.commit( 'AUTHTOKEN', null );
					return;
				}
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Create or fetch the current user's authtoken.
	 *
	 * @param {Object} context - Vuex context
	 * @return {Promise}
	 */
	newAuthtoken( context ) {
		const request = {
			url: '/api/user/authtoken/',
			method: 'POST'
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'AUTHTOKEN', success.body.token );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Delete the current user's authtoken.
	 *
	 * @param {Object} context - Vuex context
	 * @return {Promise}
	 */
	deleteAuthtoken( context ) {
		const request = {
			url: '/api/user/authtoken/',
			method: 'DELETE'
		};

		return makeApiCall( context, request ).then(
			() => {
				context.commit( 'AUTHTOKEN', null );
			},
			( failure ) => {
				if ( failure.statusCode === 404 ) {
					// Token was already deleted
					context.commit( 'AUTHTOKEN', null );
					return;
				}
				displayErrorNotification.call( this, failure );
			}
		);
	}
};

export const mutations = {
	USER_PROMISE( state, promise ) {
		state.userPromise = promise;
	},
	USER( state, user ) {
		state.user = user;
	},
	USERS( state, users ) {
		state.users = users.results;
		state.numUsers = users.count || users.length;
	},
	AUTHTOKEN( state, token ) {
		state.authtoken = token;
	}
};

export default {
	namespaced: true,
	state: {
		userPromise: null,
		user: {
			is_authenticated: false,
			csrf_token: '',
			casl: []
		},
		users: [],
		numUsers: 0,
		authtoken: null
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
