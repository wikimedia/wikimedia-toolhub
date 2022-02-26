/* eslint-disable no-unused-vars */
'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;

import LineChart from './LineChart';

describe( 'components/chart', () => {
	describe( 'LineChart', () => {
		it( 'should have configuration', () => {
			const data = LineChart.data();
			expect( data ).to.be.an( 'object' );
		} );
	} );
} );
