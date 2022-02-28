import Vue from 'vue';
import Vuex from 'vuex';
import i18n from '@/plugins/i18n';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';
import { displayErrorNotification } from '@/helpers/notifications';
import { asList, asVersion } from '@/helpers/casl';

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
	},
	LIST_REVISIONS( state, revisions ) {
		state.listRevisions = asVersion( revisions.results );
		state.numRevisions = revisions.count;
	},
	LIST_REVISION( state, revision ) {
		state.listRevision = asVersion( revision );
	},
	DIFF_REVISION( state, revision ) {
		state.diffRevision = revision;
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
				displayErrorNotification.call( this, failure );
			}
		);
	},
	getMyLists( context, page ) {
		return context.dispatch(
			'user/getUserInfo', null, { root: true }
		).then( () => {
			const params = new URLSearchParams( [
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
					displayErrorNotification.call( this, failure );
				}
			);
		} );
	},
	featureList( context, id ) {
		const request = {
			url: '/api/lists/' + id + '/feature/',
			method: 'PATCH'
		};
		return makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'getListById', id );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	unfeatureList( context, id ) {
		const request = {
			url: '/api/lists/' + id + '/unfeature/',
			method: 'PATCH'
		};
		return makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'getListById', id );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
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
				context.commit( 'CREATE_LIST', false );
				displayErrorNotification.call( this, failure );
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
				displayErrorNotification.call( this, failure );
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
				displayErrorNotification.call( this, failure );
			}
		);
	},
	getListById( context, id ) {
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
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Update list revisions state with the results obtained via the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	updateListRevisions( context, list ) {
		return context.dispatch( 'getRevisions', list ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'LIST_REVISIONS', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Fetch list revisions via the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise} Promise object with revisions data
	 */
	getRevisions( context, list ) {
		const request = {
			url: '/api/lists/' + list.id + '/revisions/?page=' + list.page
		};
		return makeApiCall( context, request );
	},
	/**
	 * Fetch list revision information from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	getListRevision( context, list ) {
		const request = {
			url: '/api/lists/' + list.id + '/revisions/' + list.revId + '/'
		};

		return makeApiCall( context, request ).then(
			( response ) => {
				context.commit( 'LIST_REVISION', response.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Fetch differences between revisions from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	getListRevisionsDiff( context, list ) {
		const request = {
			url: '/api/lists/' + list.id + '/revisions/' + list.revId + '/diff/' + list.otherId + '/'
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'DIFF_REVISION', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Undo changes between two revisions via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	async undoChangesBetweenRevisions( context, list ) {
		const id = list.revId,
			nextPage = list.page + 1,
			listRevisions = context.state.listRevisions,
			revIndex = listRevisions.findIndex( ( revision ) => revision.id === id ),
			nextIndex = parseInt( revIndex ) + 1;

		let otherId = '';

		if ( nextIndex === listRevisions.length ) {
			// Fetch more revisions to obtain other id if the revision
			// selected for an undo is last in the current list
			await context.dispatch( 'getRevisions', {
				name: tool.name, page: nextPage
			} ).then(
				( success ) => {
					const results = success.body.results;
					otherId = results[ 0 ].id; // Get rev id from the first element
				},
				( failure ) => {
					displayErrorNotification.call( this, failure );
				}
			);
		} else {
			otherId = listRevisions[ nextIndex ] && listRevisions[ nextIndex ].id;
		}

		if ( !( !!id && !!otherId ) ) {
			return;
		}

		const request = {
			url: '/api/lists/' + list.id + '/revisions/' + id + '/undo/' + otherId + '/',
			method: 'POST'
		};

		return makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateListRevisions', {
					page: list.page,
					id: list.id
				} );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Restore list to a particular revision via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	restoreListToRevision( context, list ) {
		const request = {
			url: '/api/lists/' + list.id + '/revisions/' + list.revId + '/revert/',
			method: 'POST'
		};

		return makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateListRevisions', {
					page: list.page,
					id: list.id
				} );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Hide or reveal a particular revision via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	hideRevealRevision( context, list ) {
		const request = {
			url: '/api/lists/' + list.id + '/revisions/' + list.revId + '/' + list.action + '/',
			method: 'PATCH'
		};

		return makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateListRevisions', {
					page: list.page,
					id: list.id
				} );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Mark a revision as patrolled via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @return {Promise<undefined>}
	 */
	markRevisionAsPatrolled( context, list ) {
		const request = {
			url: '/api/lists/' + list.id + '/revisions/' + list.revId + '/patrol/',
			method: 'PATCH'
		};

		return makeApiCall( context, request ).then(
			() => {
				return context.dispatch( 'updateListRevisions', {
					page: list.page,
					id: list.id
				} );
			},
			( failure ) => {
				const data = getFailurePayload( failure );
				if ( data.code === 4093 ) {
					// T301870: treat already marked as patrolled error as
					// success.
					return context.dispatch( 'updateListRevisions', {
						page: list.page,
						id: list.id
					} );
				} else {
					displayErrorNotification.call( this, failure );
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
		list: null,
		listRevisions: [],
		listRevision: 0,
		diffRevision: null
	},
	actions,
	mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
