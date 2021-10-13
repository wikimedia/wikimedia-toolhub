import Vue from 'vue';
import Vuex from 'vuex';
import i18n from '@/plugins/i18n';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';
import { asList } from '@/helpers/casl';

Vue.use( Vuex );

export const mutations = {
	FEATURED_LISTS( state, lists ) {
		state.featuredLists = asList( lists );
	},
	MY_LISTS( state, lists ) {
		state.myLists = asList( lists );
	},
	CREATE_LIST( state, list ) {
		state.listCreated = asList( list );
	},
	LIST( state, list ) {
		state.list = asList( list );
	}
};

export const actions = {
	getFeaturedLists( context, page ) {
		const request = {
			url: '/api/lists/?featured=true&page=' + page,
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'FEATURED_LISTS', data );
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
	getMyLists( context, page ) {
		const params = new URLSearchParams( [
			// FIXME: we should have a cleaner way to get the current user
			[ 'user', context.rootState.user.user.username ],
			[ 'page', page ]
		] );

		const request = {
			url: '/api/lists/?' + params.toString(),
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'MY_LISTS', data );
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
	createNewList( context, listinfo ) {
		const request = {
			url: '/api/lists/',
			method: 'POST',
			body: JSON.stringify( listinfo )
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'CREATE_LIST', data );

				this._vm.$notify.success(
					i18n.t( 'lists-listcreationsuccess', [ data.title ] ), 30000
				);
			},
			( failure ) => {
				const data = getFailurePayload( failure );
				context.commit( 'CREATE_LIST', false );

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
	editList( context, listinfo ) {
		const request = {
			url: '/api/lists/' + listinfo.id + '/',
			method: 'PUT',
			body: JSON.stringify( listinfo )
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;

				this._vm.$notify.success(
					i18n.t( 'lists-listeditingsuccess', [ data.title ] ), 30000
				);
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
	deleteList( context, id ) {
		const request = {
			url: '/api/lists/' + id + '/',
			method: 'DELETE'
		};

		return makeApiCall( context, request ).then(
			() => {
				this._vm.$notify.success(
					i18n.t( 'lists-listdeletionsuccess' ), 30000
				);
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
	getListInfo( context, id ) {
		const request = {
			url: '/api/lists/' + id + '/',
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'LIST', data );
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
	}
};

export default {
	namespaced: true,
	state: {
		featuredLists: [],
		myLists: {},
		listCreated: {},
		list: null
	},
	actions,
	mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
