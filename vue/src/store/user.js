import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';
import { asUrl } from '@/helpers/casl';

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
		const request = {
			url: '/api/user/'
		};
		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'USER', success.body );
				// Set the user's abilities
				vm.$ability.update( success.body.casl );
			},
			( failure ) => {
				const data = getFailurePayload( failure );
				this._vm.$notify.error(
					i18n.t( 'apierror', [ data ] )
				);
			}
		);
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
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	registerUrl( context, url ) {
		if ( !context.state.user.is_authenticated ) {
			return;
		}
		const request = {
			url: '/api/crawler/urls/',
			method: 'POST',
			body: JSON.stringify( { url: url } )
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'REGISTER_URL', success.body );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	unregisterUrl( context, urlObj ) {
		if ( !context.state.user.is_authenticated ) {
			return;
		}
		const request = {
			url: '/api/crawler/urls/' + urlObj.id + '/',
			method: 'DELETE'
		};

		makeApiCall( context, request ).then(
			() => {
				context.commit( 'UNREGISTER_URL', urlObj.url );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	getUrlsCreatedByUser( context, page ) {
		if ( !context.state.user.is_authenticated ) {
			this._vm.$notify.info(
				i18n.t( 'addremovetools-nologintext' )
			);
			return;
		}
		const request = {
			url: '/api/crawler/urls/self/?page=' + page,
			method: 'GET'
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'USER_CREATED_URLS', success.body );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
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
	}
};

export const mutations = {
	USER( state, user ) {
		state.user = user;
	},
	USERS( state, users ) {
		state.users = users.results;
		state.numUsers = users.count || users.length;
	},
	USER_CREATED_URLS( state, urls ) {
		state.userCreatedUrls = asUrl( urls.results );
		state.numUserCreatedUrls = urls.count;
	},
	REGISTER_URL( state, url ) {
		state.userCreatedUrls.push( asUrl( url ) );
		state.numUserCreatedUrls += 1;
	},
	UNREGISTER_URL( state, url ) {
		const index = state.userCreatedUrls.findIndex(
			( obj ) => obj.url === url
		);
		state.userCreatedUrls.splice( index, 1 );
		state.numUserCreatedUrls -= 1;
	}
};

export default {
	namespaced: true,
	state: {
		user: {
			is_authenticated: false,
			csrf_token: '',
			casl: []
		},
		users: [],
		numUsers: 0,
		userCreatedUrls: [],
		numUserCreatedUrls: 0
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
