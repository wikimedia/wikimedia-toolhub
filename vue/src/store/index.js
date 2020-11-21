import Vue from 'vue';
import Vuex from 'vuex';
import SwaggerClient from 'swagger-client';

Vue.use( Vuex );

export default new Vuex.Store( {
	state: {
		user: {
			is_authenticated: false,
			csrf_token: ''
		},
		numUserCreatedUrls: 0,
		userCreatedUrls: [],
		apiErrorMsg: ''
	},
	mutations: {
		USER( state, user ) {
			state.user = user;
		},
		USER_CREATED_URLS( state, urls ) {
			state.userCreatedUrls = urls.results;
			state.numUserCreatedUrls = urls.count;
			state.apiErrorMsg = '';
		},
		REGISTER_URL( state, urlObj ) {
			state.userCreatedUrls.push( urlObj );
			state.numUserCreatedUrls += 1;
			state.apiErrorMsg = '';
		},
		UNREGISTER_URL( state, url ) {
			const index = state.userCreatedUrls.findIndex( ( obj ) => obj.url === url );
			state.userCreatedUrls.splice( index, 1 );
			state.numUserCreatedUrls -= 1;
			state.apiErrorMsg = '';
		},
		ERROR( state, error ) {
			state.apiErrorMsg = error;
		}
	},
	actions: {
		getUserInfo( context ) {
			fetch( '/api/user/', { credentials: 'same-origin' } )
				.then( ( response ) => response.json() )
				.then( ( data ) => ( context.commit( 'USER', data ) ) );
		},
		registerUrl( context, url ) {
			if ( !this.state.user.is_authenticated ) {
				return;
			}

			const request = {
				url: '/api/crawler/urls/',
				method: 'POST',
				body: '{ "url": "' + url + '" }',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFTOKEN': this.state.user.csrf_token
				}
			};

			SwaggerClient.http( request ).then( ( response ) => {
				context.commit( 'REGISTER_URL', JSON.parse( response.text ) );
			} )
				.catch( ( err ) => context.commit( 'ERROR', err ) );
		},
		unregisterUrl( context, urlObj ) {
			if ( !this.state.user.is_authenticated ) {
				return;
			}

			const request = {
				url: '/api/crawler/urls/' + urlObj.id + '/',
				method: 'DELETE',
				headers: {
					'X-CSRFTOKEN': this.state.user.csrf_token
				}
			};

			SwaggerClient.http( request ).then( () => {
				context.commit( 'UNREGISTER_URL', urlObj.url );
			} )
				.catch( ( err ) => context.commit( 'ERROR', err ) );
		},
		getUrlsCreatedByUser( context, page ) {
			if ( !this.state.user.is_authenticated ) {
				return;
			}

			const request = {
				url: '/api/crawler/urls/self/?page=' + page,
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			};

			SwaggerClient.http( request ).then( ( response ) => {
				context.commit( 'USER_CREATED_URLS', response.body );
			} )
				.catch( ( err ) => context.commit( 'ERROR', err ) );
		},
		setLocale( context, locale ) {
			const request = {
				url: '/api/user/locale/',
				method: 'POST',
				mode: 'same-origin',
				body: JSON.stringify( { language: locale } ),
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFTOKEN': this.state.user.csrf_token
				}
			};
			SwaggerClient.http( request );
		}
	},
	modules: {
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
} );
