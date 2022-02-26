'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { actions, mutations } from './vuex';

describe( 'notify/vuex', () => {
	describe( 'actions', () => {
		it( 'message', () => {
			const commit = sinon.spy();

			const payload = {
				message: 'test-message',
				type: 'info',
				prominent: false
			};

			const mid = actions.message( { commit }, payload );

			expect( commit ).to.have.been.calledOnce;
			expect( commit ).to.have.been.calledWithExactly(
				'onMessage',
				Object.assign( payload, { id: mid, timeoutID: null } )
			);
		} );

		it( 'message with timeout', () => {
			const commit = sinon.spy();
			const expectTimeout = 12345;
			const setTimeout = sinon.stub( window, 'setTimeout' )
				.returns( expectTimeout );

			const payload = {
				message: 'test-message',
				type: 'info',
				prominent: false,
				timeout: 31337
			};

			const mid = actions.message( { commit }, payload );

			expect( setTimeout ).to.have.been.calledOnce;
			expect( setTimeout ).to.have.been.calledWithExactly(
				sinon.match.func,
				31337
			);
			expect( setTimeout ).to.have.been.calledBefore( commit );
			expect( commit ).to.have.been.calledOnce;
			expect( commit ).to.have.been.calledWithExactly(
				'onMessage', {
					id: mid,
					message: payload.message,
					type: payload.type,
					prominent: payload.prominent,
					timeoutID: expectTimeout
				}
			);
		} );

		it( 'success', () => {
			const dispatch = sinon.stub();
			const payload = {
				message: 'test-message'
			};
			actions.success( { dispatch }, payload );

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledWithExactly(
				'message',
				Object.assign( payload, { timeout: null, type: 'success' } )
			);
		} );

		it( 'info', () => {
			const dispatch = sinon.stub();
			const payload = {
				message: 'test-message'
			};
			actions.info( { dispatch }, payload );

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledWithExactly(
				'message',
				Object.assign( payload, { timeout: null, type: 'info' } )
			);
		} );

		it( 'warning', () => {
			const dispatch = sinon.stub();
			const payload = {
				message: 'test-message'
			};
			actions.warning( { dispatch }, payload.message );

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledWithExactly(
				'message',
				Object.assign( payload, { type: 'warning', prominent: true } )
			);
		} );

		it( 'error', () => {
			const dispatch = sinon.stub();
			const payload = {
				message: 'test-message'
			};
			actions.error( { dispatch }, payload.message );

			expect( dispatch ).to.have.been.calledOnce;
			expect( dispatch ).to.have.been.calledWithExactly(
				'message',
				Object.assign( payload, { type: 'error', prominent: true } )
			);
		} );

		it( 'clearMessage', () => {
			const commit = sinon.spy();

			actions.clearMessage( { commit }, 31337 );

			expect( commit ).to.have.been.calledOnce;
			expect( commit ).to.have.been.calledWithExactly(
				'onClearMessage', 31337
			);
		} );
	} );

	describe( 'mutations', () => {
		it( 'onMessage', () => {
			const state = { messages: [] };

			const payload = {
				id: 10100111001,
				message: 'test-message',
				type: 'success',
				prominent: false,
				timeoutID: false
			};
			mutations.onMessage( state, payload );

			expect( state.messages ).to.deep.equal( [ payload ] );
		} );

		it( 'onClearMessage', () => {
			const state = { messages: [ { id: 31337 } ] };

			mutations.onClearMessage( state, 31337 );
			expect( state.messages ).to.be.an( 'array' ).that.is.empty;
		} );

		it( 'onClearMessage with unknown id', () => {
			const state = { messages: [] };

			mutations.onClearMessage( state, 1337 );
			expect( state.messages ).to.be.an( 'array' ).that.is.empty;
		} );

		it( 'onClearMessage with timeout', () => {
			const clearTimeout = sinon.stub( window, 'clearTimeout' );

			const state = { messages: [
				{ id: 1, timeoutID: false },
				{ id: 2, timeoutID: 1337 },
				{ id: 3, timeoutID: false }
			] };

			mutations.onClearMessage( state, 2 );

			expect( clearTimeout ).to.have.been.calledOnce;
			expect( clearTimeout ).to.have.been.calledWithExactly( 1337 );
			expect( state.messages ).to.be.an( 'array' )
				.that.has.lengthOf( 2 )
				.but.not.deep.include( { id: 2, timeoutID: 1337 } );
		} );
	} );

} );
