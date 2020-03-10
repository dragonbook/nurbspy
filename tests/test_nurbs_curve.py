""" Unit tests for the NURBS curve computations """

# -------------------------------------------------------------------------------------------------------------------- #
# Importing packages
# -------------------------------------------------------------------------------------------------------------------- #
import sys
import os
import time
import pdb
import numpy as np
import nurbspy as nrb


# -------------------------------------------------------------------------------------------------------------------- #
# Prepare the NURBS curve test suite
# -------------------------------------------------------------------------------------------------------------------- #
def test_nurbs_curve_scalar_input():

    """ Test the Bezier curve computation in scalar mode for real and complex input """

    # Define the array of control points
    P = np.zeros((2, 2))
    P[:, 0] = [0.00, 0.00]
    P[:, 1] = [1.00, 1.00]

    # Create the NURBS curve
    bezierCurve = nrb.NurbsCurve(control_points=P)

    # Check real
    values_real = bezierCurve.get_value(u=0.5).flatten()
    assert np.sum((values_real - np.asarray([0.5, 0.5])) ** 2) ** (1 / 2) < 1e-6

    # Check complex
    values_complex = bezierCurve.get_value(u=0.5 + 0.5j).flatten()
    assert np.sum((values_complex - np.asarray([0.5 + 0.5j, 0.5 + 0.5j])) ** 2) ** (1 / 2) < 1e-6


def test_nurbs_curve_endpoint_property():

    """ Test the NURBS curve end-point interpolation property """

    # Define the array of control points
    P = np.zeros((3, 4))
    P[:, 0] = [1.00, 2.00, 1.00]
    P[:, 1] = [2.00, 1.00, 2.00]
    P[:, 2] = [3.00, 2.00, 3.00]
    P[:, 3] = [4.00, 1.00, 4.00]

    # Define the array of control point weights
    W = np.asarray([2.00, 3.00, 1.00, 2.00])

    # Maximum index of the control points (counting from zero)
    n = np.shape(P)[1] - 1

    # Define the order of the basis polynomials
    p = 2

    # Define the knot vector (clamped spline)
    # p+1 zeros, n-p equispaced points between 0 and 1, and p+1 ones. In total r+1 points where r=n+p+1
    U = np.concatenate((np.zeros(p), np.linspace(0, 1, n - p + 2), np.ones(p)))

    # Create the NURBS curve
    nurbsCurve = nrb.NurbsCurve(control_points=P, weights=W, degree=p, knots=U)

    # Check the corner point values
    assert np.sum((nurbsCurve.get_value(u=0.00).flatten() - P[:,  0]) ** 2) ** (1 / 2) < 1e-6
    assert np.sum((nurbsCurve.get_value(u=1.00).flatten() - P[:, -1]) ** 2) ** (1 / 2) < 1e-6


def test_nurbs_curve_example_1():

    """ Test the B-Spline curve computation against a known example (Ex2.2 from the NURBS book) """

    # Define the array of control points
    P2 = np.asarray([1, 3, 5])
    P3 = np.asarray([2, 1, 4])
    P4 = np.asarray([3, 0, 6])
    P = np.zeros((3, 8))
    P[:, 2] = P2
    P[:, 3] = P3
    P[:, 4] = P4

    # Define the order of the basis polynomials
    p = 2

    # Define the knot vector (clamped spline)
    # p+1 zeros, n-p equispaced points between 0 and 1, and p+1 ones. In total r+1 points where r=n+p+1
    #                 u0    u1    u2    u3    u4    u5    u6    u7    u8    u9   u10
    U = np.asarray([0.00, 0.00, 0.00, 1.00, 2.00, 3.00, 4.00, 4.00, 5.00, 5.00, 5.00])

    # Create the B-Spline curve
    myBSpline = nrb.NurbsCurve(control_points=P, knots=U, degree=p)

    # Evaluate the B-Spline curve numerically
    u = 5/2   # u-parameter
    values_numeric = myBSpline.get_value(u)

    # Evaluate the B-Spline curve analytically (NURBS book page 82)
    values_analytic = (1/8*P2 + 6/8*P3 + 1/8*P4)[:, np.newaxis]

    # Check the error
    error = np.sum((values_analytic - values_numeric) ** 2) ** (1 / 2)
    print('The two-norm of the evaluation error is         :  ', error)
    assert error < 1e-8


def test_nurbs_curve_example_2():

    """ Test the NURBS curve value against a known example (NURBS book section 7.5) """

    # Create a circle using 4 arcs of 90 degrees
    # Define the array of control points
    P = np.zeros((2, 9))
    P[:, 0] = [1.00, 0.00]
    P[:, 1] = [1.00, 1.00]
    P[:, 2] = [0.00, 1.00]
    P[:, 3] = [-1.00, 1.00]
    P[:, 4] = [-1.00, 0.00]
    P[:, 5] = [-1.00, -1.00]
    P[:, 6] = [0.00, -1.00]
    P[:, 7] = [1.00, -1.00]
    P[:, 8] = [1.00, 0.00]

    # Define the array of control point weights
    W = np.asarray([1, np.sqrt(2) / 2, 1, np.sqrt(2) / 2, 1, np.sqrt(2) / 2, 1, np.sqrt(2) / 2, 1])

    # Define the order of the basis polynomials
    p = 2

    # Define the knot vector (clamped spline)
    # p+1 zeros, n minus p equispaced points between 0 and 1, and p+1 ones.  In total r+1 points where r=n+p+1
    U = np.asarray([0, 0, 0, 1 / 4, 1 / 4, 1 / 2, 1 / 2, 3 / 4, 3 / 4, 1, 1, 1])

    # Create the NURBS curve
    myCircle = nrb.NurbsCurve(P, W, p, U)

    # Define the u-parametrization
    u = np.linspace(0, 1, 101)

    # Check the radius error
    coords = myCircle.get_value(u)
    radius_error = np.sum((np.sum((coords)**2, axis=0) - 1) ** 2) ** (1/2)
    print('The two-norm of the evaluation error is         :  ', radius_error)
    assert radius_error < 1e-8


def test_nurbs_curve_example_3():

    """ Test the NURBS curve value against a known example (NURBS book section 7.5) """

    # Create a circle using 3 arcs of 120 degrees
    # Define the array of control points
    a = np.cos(np.pi / 6)
    P = np.zeros((2, 7))
    P[:, 0] = [a, 1 / 2]
    P[:, 1] = [0, 2]
    P[:, 2] = [-a, 1 / 2]
    P[:, 3] = [-2 * a, -1]
    P[:, 4] = [0, -1]
    P[:, 5] = [2 * a, -1]
    P[:, 6] = [a, 1 / 2]

    # Define the array of control point weights
    W = np.asarray([1, 1 / 2, 1, 1 / 2, 1, 1 / 2, 1])

    # Define the order of the basis polynomials
    p = 2

    # Define the knot vector (clamped spline)
    # p+1 zeros, n minus p equispaced points between 0 and 1, and p+1 ones.  In total r+1 points where r=n+p+1
    U = np.asarray([0, 0, 0, 1 / 3, 1 / 3, 2 / 3, 2 / 3, 1, 1, 1])

    # Create the NURBS curve
    myCircle = nrb.NurbsCurve(P, W, p, U)

    # Define the u-parametrization
    u = np.linspace(0, 1, 101)

    # Check the radius error
    coords = myCircle.get_value(u)
    radius_error = np.sum((np.sum((coords)**2, axis=0) - 1) ** 2) ** (1/2)
    print('The two-norm of the evaluation error is         :  ', radius_error)
    assert radius_error < 1e-8


def test_nurbs_curve_example_4():

    """ Test the computation of a circular NURBS curve value, curvature and arc-length in 2D """

    # Set defining parameters
    O = np.asarray([0.00, 1.00])                 # Circle center
    X = np.asarray([1.00, 0.00])                 # Abscissa direction
    Y = np.asarray([0.00, 1.00])                 # Ordinate direction
    R = 0.5                                      # Circle radius
    theta_start = 1 / 6 * np.pi                  # Start angle
    theta_end = 3 / 2 * np.pi - 1 / 6 * np.pi    # End angle

    # Create and plot the circular arc
    my_circular_arc = nrb.CircularArc(O, X, Y, R, theta_start, theta_end).NurbsCurve

    # Define the u-parametrization
    u = np.linspace(0, 1, 101)

    # Check the radius error
    coords = my_circular_arc.get_value(u)
    radius_error = np.sum((np.sum((coords-O[:, np.newaxis])**2, axis=0) - R**2) ** 2) ** (1/2)
    print('The two-norm of the radius error is             :  ', radius_error)
    assert radius_error < 1e-8

    # CHeck the curvature error
    curvature = my_circular_arc.get_curvature(u)
    curvature_error = np.sum((curvature - 1 / R) ** 2) ** (1 / 2)
    print("The two-norm of the curvature error is          :  ", curvature_error)
    assert curvature_error < 1e-8

    # Check the arc length error
    arc_length = my_circular_arc.get_arclength()
    arc_length_error = arc_length - R * np.abs(theta_end - theta_start)
    print("The arc length computation error is             :  ", arc_length_error)
    assert arc_length_error < 1e-2


def test_nurbs_curve_example_5():

    """ Test the computation of a circular NURBS curve value, curvature and arc-length in 3D """

    # Set defining parameters
    O = np.asarray([0.00, 0.00, 0.50])      # Circle center
    X = np.asarray([3.00, 0.00, 0.00])      # Abscissa direction
    Y = np.asarray([0.00, 1.00, 0.00])      # Ordinate direction
    R = 0.5                                 # Circle radius
    theta_start = 0.00                      # Start angle
    theta_end = np.pi/2                     # End angle

    # Create and plot the circular arc
    my_circular_arc = nrb.CircularArc(O, X, Y , R, theta_start, theta_end).NurbsCurve

    # Define the u-parametrization
    u = np.linspace(0, 1, 101)

    # Check the radius error
    coords = my_circular_arc.get_value(u)
    radius_error = np.sum((np.sum((coords-O[:, np.newaxis])**2, axis=0) - R**2) ** 2) ** (1/2)
    print('The two-norm of the radius error is             :  ', radius_error)
    assert radius_error < 1e-8

    # CHeck the curvature error
    curvature = my_circular_arc.get_curvature(u)
    curvature_error = np.sum((curvature - 1 / R) ** 2) ** (1 / 2)
    print("The two-norm of the curvature error is          :  ", curvature_error)
    assert curvature_error < 1e-8

    # Check the arc length error
    arc_length = my_circular_arc.get_arclength()
    arc_length_error = arc_length - R * np.abs(theta_end - theta_start)
    print("The arc length computation error is             :  ", arc_length_error)
    assert arc_length_error < 1e-2

    # Check the Frenet-Serret frame of reference computation (starting point)
    assert np.sum((my_circular_arc.get_tangent(u=0.00)  - np.asarray([0, 1, 0])[:, np.newaxis]) ** 2) ** (1 / 2) < 1e-6
    assert np.sum((my_circular_arc.get_normal(u=0.00)  - np.asarray([-1, 0, 0])[:, np.newaxis]) ** 2) ** (1 / 2) < 1e-6
    assert np.sum((my_circular_arc.get_binormal(u=0.00) - np.asarray([0, 0, 1])[:, np.newaxis]) ** 2) ** (1 / 2) < 1e-6

    # Check the Frenet-Serret frame of reference computation (end point)
    assert np.sum((my_circular_arc.get_tangent(u=1.00)  - np.asarray([-1, 0, 0])[:, np.newaxis]) ** 2) ** (1 / 2) < 1e-6
    assert np.sum((my_circular_arc.get_normal(u=1.00)   - np.asarray([0, -1, 0])[:, np.newaxis]) ** 2) ** (1 / 2) < 1e-6
    assert np.sum((my_circular_arc.get_binormal(u=1.00) - np.asarray([0, 0, 1])[:, np.newaxis]) ** 2) ** (1 / 2) < 1e-6


def test_nurbs_curve_zeroth_derivative():

    """ Test that the zero-th derivative agrees with the function evaluation """

    # Define the array of control points
    P = np.zeros((3, 5))
    P[:, 0] = [0.00, 0.00, 0.00]
    P[:, 1] = [0.00, 0.30, 0.05]
    P[:, 2] = [0.25, 0.30, 0.30]
    P[:, 3] = [0.50, 0.30, -0.05]
    P[:, 4] = [0.50, 0.10, 0.10]

    # Maximum index of the control points (counting from zero)
    n = np.shape(P)[1] - 1

    # Define the array of control point weights
    W = np.asarray([1, 1, 3, 1, 1])

    # Define the order of the basis polynomials
    # Linear (p = 1), Quadratic (p = 2), Cubic (p = 3), etc.
    # Set p = n (number of control points minus one) to obtain a Bezier
    p = 3

    # Define the knot vector (clamped spline)
    # p+1 zeros, n-p equispaced points between 0 and 1, and p+1 ones. In total r+1 points where r=n+p+1
    U = np.concatenate((np.zeros(p), np.linspace(0, 1, n - p + 2), np.ones(p)))

    # Create the NURBS curve
    nurbs3D = nrb.NurbsCurve(control_points=P, weights=W, degree=p, knots=U)

    # Define the u-parametrization
    u = np.linspace(0, 1, 101)

    # Compute the NURBS curve values
    C  = nurbs3D.get_value(u)
    dC = nurbs3D.get_derivative(u, order=0)

    # Check the error
    error = np.sum((C - dC) ** 2) ** (1 / 2) / u.size
    print('The two-norm of the zeroth derivative error is  :  ', error)
    assert error < 1e-8


def test_nurbs_curve_first_derivative_cs():

    """ Test the first derivative against the complex step method """

    # Define the array of control points
    P = np.zeros((3, 5))
    P[:, 0] = [0.00, 0.00, 0.00]
    P[:, 1] = [0.00, 0.30, 0.05]
    P[:, 2] = [0.25, 0.30, 0.30]
    P[:, 3] = [0.50, 0.30, -0.05]
    P[:, 4] = [0.50, 0.10, 0.10]

    # Maximum index of the control points (counting from zero)
    n = np.shape(P)[1] - 1

    # Define the array of control point weights
    W = np.asarray([1, 1, 3, 1, 1])

    # Define the order of the basis polynomials
    # Linear (p = 1), Quadratic (p = 2), Cubic (p = 3), etc.
    # Set p = n (number of control points minus one) to obtain a Bezier
    p = 3

    # Define the knot vector (clamped spline)
    # p+1 zeros, n-p equispaced points between 0 and 1, and p+1 ones. In total r+1 points where r=n+p+1
    U = np.concatenate((np.zeros(p), np.linspace(0, 1, n - p + 2), np.ones(p)))

    # Create the NURBS curve
    nurbs3D = nrb.NurbsCurve(control_points=P, weights=W, degree=p, knots=U)

    # Define the u-parametrization
    u = np.linspace(0, 1, 101)
    h = 1e-12

    # Compute the NURBS analytic derivative
    dC_analytic = nurbs3D.get_derivative(u, order=1)

    # Compute the NURBS complex step derivative
    dC_complex_step = np.imag(nurbs3D.get_value(u + h * 1j)) / h

    # Check the error
    error = np.sum((dC_analytic - dC_complex_step) ** 2) ** (1 / 2) / u.size
    print('The two-norm of the first derivative error is   :  ', error)
    assert error < 1e-8


def test_nurbs_curve_first_derivative_cfd():

    """ Test the first derivative against central finite differences """

    # Define the array of control points
    P = np.zeros((3, 5))
    P[:, 0] = [0.00, 0.00, 0.00]
    P[:, 1] = [0.00, 0.30, 0.05]
    P[:, 2] = [0.25, 0.30, 0.30]
    P[:, 3] = [0.50, 0.30, -0.05]
    P[:, 4] = [0.50, 0.10, 0.10]

    # Maximum index of the control points (counting from zero)
    n = np.shape(P)[1] - 1

    # Define the array of control point weights
    W = np.asarray([1, 1, 3, 1, 1])

    # Define the order of the basis polynomials
    # Linear (p = 1), Quadratic (p = 2), Cubic (p = 3), etc.
    # Set p = n (number of control points minus one) to obtain a Bezier
    p = 3

    # Define the knot vector (clamped spline)
    # p+1 zeros, n-p equispaced points between 0 and 1, and p+1 ones. In total r+1 points where r=n+p+1
    U = np.concatenate((np.zeros(p), np.linspace(0, 1, n - p + 2), np.ones(p)))

    # Create the NURBS curve
    nurbs3D = nrb.NurbsCurve(control_points=P, weights=W, degree=p, knots=U)

    # Define a new u-parametrization suitable for finite differences
    h = 1e-5
    hh = h + h ** 2
    Nu = 1000
    u = np.linspace(0.00 + hh, 1.00 - hh, Nu)  # Make sure that the limits [0, 1] also work when making changes

    # Compute the NURBS analytic derivative
    dC_analytic = nurbs3D.get_derivative(u, order=1)

    # Compute the NURBS central finite differences derivative
    a = -1 / 2 * nurbs3D.get_value(u - h)
    b = +1 / 2 * nurbs3D.get_value(u + h)
    dC_cfd = (a + b) / h

    # Check the error
    error = np.sum((dC_analytic - dC_cfd) ** 2) ** (1 / 2) / u.size
    print('The two-norm of the first derivative error is   :  ', error)
    assert error < 1e-6


def test_nurbs_curve_second_derivative_cfd():

    """ Test the first derivative against central finite differences """

    # Define the array of control points
    P = np.zeros((3, 5))
    P[:, 0] = [0.00, 0.00, 0.00]
    P[:, 1] = [0.00, 0.30, 0.05]
    P[:, 2] = [0.25, 0.30, 0.30]
    P[:, 3] = [0.50, 0.30, -0.05]
    P[:, 4] = [0.50, 0.10, 0.10]

    # Maximum index of the control points (counting from zero)
    n = np.shape(P)[1] - 1

    # Define the array of control point weights
    W = np.asarray([1, 1, 3, 1, 1])

    # Define the order of the basis polynomials
    # Linear (p = 1), Quadratic (p = 2), Cubic (p = 3), etc.
    # Set p = n (number of control points minus one) to obtain a Bezier
    p = 3

    # Define the knot vector (clamped spline)
    # p+1 zeros, n-p equispaced points between 0 and 1, and p+1 ones. In total r+1 points where r=n+p+1
    U = np.concatenate((np.zeros(p), np.linspace(0, 1, n - p + 2), np.ones(p)))

    # Create the NURBS curve
    nurbs3D = nrb.NurbsCurve(control_points=P, weights=W, degree=p, knots=U)

    # Define a new u-parametrization suitable for finite differences
    h = 1e-5
    hh = h + h ** 2
    Nu = 1000
    u = np.linspace(0.00 + hh, 1.00 - hh, Nu)  # Make sure that the limits [0, 1] also work when making changes

    # Compute the NURBS analytic derivative
    dC_analytic = nurbs3D.get_derivative(u, order=2)

    # Compute the NURBS central finite differences derivative
    a = +1 * nurbs3D.get_value(u - h)
    b = -2 * nurbs3D.get_value(u)
    c = +1 * nurbs3D.get_value(u + h)
    dC_cfd = (a + b + c) / h**2

    # Check the error
    error = np.sum((dC_analytic - dC_cfd) ** 2) ** (1 / 2) / u.size
    print('The two-norm of the second derivative error is  :  ', error)
    assert error < 1e-6



# -------------------------------------------------------------------------------------------------------------------- #
# Check the functions manually
# -------------------------------------------------------------------------------------------------------------------- #
# test_nurbs_curve_scalar_input()
# test_nurbs_curve_endpoint_property()
# test_nurbs_curve_example_1()
# test_nurbs_curve_example_2()
# test_nurbs_curve_example_3()
# test_nurbs_curve_example_4()
# test_nurbs_curve_example_5()
# test_nurbs_curve_zeroth_derivative()
# test_nurbs_curve_first_derivative_cs()
# test_nurbs_curve_first_derivative_cfd()
# test_nurbs_curve_second_derivative_cfd()
