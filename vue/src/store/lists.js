import Vue from 'vue';
import Vuex from 'vuex';
import i18n from '@/plugins/i18n';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger';
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
	PUBLISHED_LISTS( state, lists ) {
		state.publishedLists = asList( lists );
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
		const request = { url: '/api/lists/?featured=true&page=' + page };

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
	getPublishedLists( context, page ) {
		const request = { url: '/api/lists/?published=true&page=' + page };

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'PUBLISHED_LISTS', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Fetch a user's lists
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} list - list info
	 * @param {number} list.page - a page number within the paginated result set
	 * @param {number} list.pageSize - number of lists to return per page
	 * @return {Promise<undefined>}
	 */
	getMyLists( context, { page, pageSize } ) {
		return context.dispatch(
			'user/getUserInfo', null, { root: true }
		).then( () => {
			const params = new URLSearchParams( [
				[ 'user', context.rootState.user.user.username ],
				[ 'page', page ],
				[ 'page_size', pageSize ]
			] );

			const request = { url: '/api/lists/?' + params.toString() };

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
		const request = { url: '/api/lists/' + id + '/' };

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
	 * @param {Object} payload
	 * @param {number} payload.id - list id
	 * @param {number} payload.revId - starting revision id
	 * @param {number} payload.prevRevId - ending revision id
	 * @return {Promise<undefined>}
	 */
	undoChangesBetweenRevisions( context, { id, revId, prevRevId } ) {
		if ( !( !!revId && !!prevRevId ) ) {
			return;
		}

		const request = {
			url: '/api/lists/' + id + '/revisions/' + revId + '/undo/' + prevRevId + '/',
			method: 'POST'
		};

		return makeApiCall( context, request ).catch(
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

		return makeApiCall( context, request ).catch(
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

		return makeApiCall( context, request ).catch(
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

		return makeApiCall( context, request ).catch(
			( failure ) => {
				const data = getFailurePayload( failure );
				if ( data.code === 4093 ) {
					// T301870: treat already marked as patrolled error as
					// success and return
					return;
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
		publishedLists: {},
		listCreated: {},
		list: null,
		listRevisions: [],
		listRevision: 0,
		numRevisions: 0,
		diffRevision: null
	},
	actions,
	mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
