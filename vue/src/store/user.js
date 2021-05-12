import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';
import { asUrl, asApp, asToken } from '@/helpers/casl';

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
	},
	registerApp( context, app ) {
		const request = {
			url: '/api/oauth/applications/',
			method: 'POST',
			body: JSON.stringify( { name: app.name, redirect_url: app.url } )
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'REGISTER_APP', success.body );

				this._vm.$notify.success(
					i18n.t( 'developersettings-appregistersuccesstext', [ success.body.name ] )
				);
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
	listClientApps( context, page ) {
		const request = {
			url: '/api/oauth/applications?page=' + page,
			method: 'GET'
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'CLIENT_APPS', success.body );
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
	updateClientApp( context, app ) {
		const request = {
			url: '/api/oauth/applications/' + app.clientId + '/',
			method: 'PATCH',
			body: JSON.stringify( { redirect_url: app.redirectUrl } )
		};

		makeApiCall( context, request ).then(
			() => {
				this._vm.$notify.success(
					i18n.t( 'developersettings-appupdatesuccess', [ app.clientId ] )
				);
			},
			() => {
				this._vm.$notify.error(
					i18n.t( 'developersettings-appupdateerror', [ app.clientId ] )
				);
			}
		);
	},
	deleteClientApp( context, clientId ) {
		const request = {
			url: '/api/oauth/applications/' + clientId,
			method: 'DELETE'
		};

		makeApiCall( context, request ).then(
			() => {
				context.commit( 'DELETE_CLIENT_APP', clientId );

				this._vm.$notify.error(
					i18n.t( 'appdeleted', [ clientId ] )
				);
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
	listAuthorizedApps( context, page ) {
		const request = {
			url: '/api/oauth/authorized?page=' + page,
			method: 'GET'
		};

		makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'AUTHORIZED_APPS', success.body );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					JSON.parse( failure.response.data ) :
					failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	deleteAuthorizedApp( context, id ) {
		const request = {
			url: '/api/oauth/authorized/' + id,
			method: 'DELETE'
		};

		makeApiCall( context, request ).then(
			() => {
				context.commit( 'DELETE_AUTHORIZED_APP', id );

				this._vm.$notify.error(
					i18n.t( 'appdeleted', [ id ] )
				);
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					JSON.parse( failure.response.data ) :
					failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	}
};

export const mutations = {
	USER( state, user ) {
		state.user = user;
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
	},
	REGISTER_APP( state, app ) {
		const application = asApp( app );
		state.clientAppCreated = application;
		state.clientApps.push( application );
		state.numClientApps += 1;
	},
	CLIENT_APPS( state, apps ) {
		state.clientApps = asApp( apps.results );
		state.numClientApps = apps.count;
	},
	DELETE_CLIENT_APP( state, clientId ) {
		const index = state.clientApps.findIndex(
			( obj ) => obj.client_id === clientId
		);
		state.clientApps.splice( index, 1 );
		state.numClientApps -= 1;
	},
	AUTHORIZED_APPS( state, apps ) {
		state.authorizedApps = asToken( apps.results );
		state.numAuthorizedApps = apps.count;
	},
	DELETE_AUTHORIZED_APP( state, id ) {
		const index = state.authorizedApps.findIndex(
			( obj ) => obj.id === id
		);
		state.authorizedApps.splice( index, 1 );
		state.numAuthorizedApps -= 1;
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
		userCreatedUrls: [],
		numUserCreatedUrls: 0,
		clientApps: [],
		numClientApps: 0,
		authorizedApps: [],
		numAuthorizedApps: 0,
		clientAppCreated: {}
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
