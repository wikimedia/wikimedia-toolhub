import Vue from 'vue';
import Vuex from 'vuex';
import i18n from '@/plugins/i18n';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';

Vue.use( Vuex );

export const mutations = {
	FEATURED_LISTS( state, lists ) {
		state.featuredLists = lists;
	},
	PRIVATE_LISTS( state, lists ) {
		state.privateLists = lists;
	},
	CREATE_LIST( state, list ) {
		state.listCreated = list;
	},
	LIST( state, list ) {
		state.list = list;
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
	getPrivateLists( context, page ) {
		const request = {
			url: '/api/lists/?published=false&page=' + page,
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'PRIVATE_LISTS', data );
			},
			( failure ) => {
				const data = getFailurePayload( failure );
				context.commit( 'PRIVATE_LIST', false );

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
		privateLists: [],
		listCreated: {},
		list: null
	},
	actions,
	mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
