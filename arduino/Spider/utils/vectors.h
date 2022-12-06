#pragma once

#include "math.h"

template<typename T>
class Vector {
public:
    T x;
    T y;
    T z;

    // Constructors

    // Vectors default to 0, 0, 0.
    Vector() {
        x = 0;
        y = 0;
        z = 0;
    }

    // Construct with values, 3D
    Vector(T ax, T ay, T az) {
        x = ax;
        y = ay;
        z = az;
    }

    // Construct with values, 2D
    Vector(T ax, T ay) {
        x = ax;
        y = ay;
        z = 0.;
    }

    // Copy constructor
    Vector(const Vector& o) {
        x = o.x;
        y = o.y;
        z = o.z;
    }

    Vector& operator=(const Vector&) = default;

    // Addition

    Vector operator+(const Vector& o) {
        return Vector(x + o.x, y + o.y, z + o.z);
    }

    Vector& operator+=(const Vector& o) {
        x += o.x;
        y += o.y;
        z += o.z;
        return *this;
    }

    // Subtraction

    Vector operator-() {
        return Vector(-x, -y, -z);
    }

    Vector operator-(const Vector o) {
        return Vector(x - o.x, y - o.y, z - o.z);
    }

    Vector& operator-=(const Vector o) {
        x -= o.x;
        y -= o.y;
        z -= o.z;
        return *this;
    }

    // Multiplication by scalars

    Vector operator*(const T s) {
        return Vector(x * s, y * s, z * s);
    }

    Vector& operator*=(const T s) {
        x *= s;
        y *= s;
        z *= s;
        return *this;
    }

    // Division by scalars

    Vector operator/(const T s) {
        return Vector(x / s, y / s, z / s);
    }

    Vector& operator/=(const T s) {
        x /= s;
        y /= s;
        z /= s;
        return *this;
    }

    // Dot product

    T operator*(const Vector o) {
        return (x * o.x) + (y * o.y) + (z * o.z);
    }

    // An in-place dot product does not exist because
    // the result is not a vector.

    // Cross product

    Vector operator^(const Vector o) {
        T nx = y * o.z - o.y * z;
        T ny = z * o.x - o.z * x;
        T nz = x * o.y - o.x * y;
        return Vector(nx, ny, nz);
    }

    Vector& operator^=(const Vector o) {
        T nx = y * o.z - o.y * z;
        T ny = z * o.x - o.z * x;
        T nz = x * o.y - o.x * y;
        x = nx;
        y = ny;
        z = nz;
        return *this;
    }

    // Other functions

    // Length of vector
    T magnitude() {
        return sqrt(magnitude_sqr());
    }

    // Length of vector squared
    T magnitude_sqr() {
        return (x * x) + (y * y) + (z * z);
    }

    // Returns a normalised copy of the vector
    // Will break if it's length is 0
    Vector normalised() {
        return Vector(*this) / magnitude();
    }

    // Modified the vector so it becomes normalised
    Vector& normalise() {
        (*this) /= magnitude();
        return *this;
    }

};

using Vectorf = Vector<float>;
using Vectord = Vector<double>;
