import {
  Injectable,
  UnauthorizedException,
  ConflictException,
  BadRequestException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../../prisma/prisma.service';
import { UsersService } from '../users/users.service';

export interface TokenPayload {
  sub: string;
  email: string;
  role: string;
  companyId: string;
  clientId?: string;
}

export interface Tokens {
  accessToken: string;
  refreshToken: string;
}

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
    private readonly usersService: UsersService,
  ) {}

  async validateUser(email: string, password: string) {
    const user = await this.usersService.findByEmail(email);
    if (!user || !user.passwordHash) {
      return null;
    }

    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      return null;
    }

    return user;
  }

  async login(user: any) {
    const tokens = await this.generateTokens(user);
    await this.saveRefreshToken(user.id, tokens.refreshToken);

    return {
      user: this.sanitizeUser(user),
      ...tokens,
    };
  }

  async register(data: {
    email: string;
    password: string;
    fullName: string;
    companyName: string;
    companyCnpj: string;
  }) {
    // Check if user already exists
    const existingUser = await this.usersService.findByEmail(data.email);
    if (existingUser) {
      throw new ConflictException('Email already registered');
    }

    // Check if company already exists
    const existingCompany = await this.prisma.company.findUnique({
      where: { cnpj: data.companyCnpj },
    });
    if (existingCompany) {
      throw new ConflictException('Company CNPJ already registered');
    }

    // Hash password
    const passwordHash = await bcrypt.hash(data.password, 12);

    // Create company and user in transaction
    const result = await this.prisma.$transaction(async (tx) => {
      const company = await tx.company.create({
        data: {
          name: data.companyName,
          cnpj: data.companyCnpj,
        },
      });

      const user = await tx.user.create({
        data: {
          email: data.email,
          passwordHash,
          fullName: data.fullName,
          role: 'ADMIN',
          status: 'ACTIVE',
          company: {
            connect: { id: company.id },
          },
        },
      });

      return { company, user };
    });

    const tokens = await this.generateTokens(result.user);
    await this.saveRefreshToken(result.user.id, tokens.refreshToken);

    return {
      user: this.sanitizeUser(result.user),
      company: result.company,
      ...tokens,
    };
  }

  async refreshTokens(refreshToken: string) {
    const storedToken = await this.prisma.refreshToken.findUnique({
      where: { token: refreshToken },
      include: { user: true },
    });

    if (!storedToken || storedToken.revokedAt || storedToken.expiresAt < new Date()) {
      throw new UnauthorizedException('Invalid or expired refresh token');
    }

    const user = storedToken.user;
    if (user.status !== 'ACTIVE') {
      throw new UnauthorizedException('User account is not active');
    }

    // Revoke old token
    await this.prisma.refreshToken.update({
      where: { id: storedToken.id },
      data: { revokedAt: new Date() },
    });

    // Generate new tokens
    const tokens = await this.generateTokens(user);
    await this.saveRefreshToken(user.id, tokens.refreshToken);

    return tokens;
  }

  async logout(userId: string, refreshToken?: string) {
    if (refreshToken) {
      await this.prisma.refreshToken.updateMany({
        where: { token: refreshToken, userId },
        data: { revokedAt: new Date() },
      });
    } else {
      // Revoke all user tokens
      await this.prisma.refreshToken.updateMany({
        where: { userId, revokedAt: null },
        data: { revokedAt: new Date() },
      });
    }
  }

  async changePassword(userId: string, currentPassword: string, newPassword: string) {
    const user = await this.usersService.findById(userId);
    if (!user || !user.passwordHash) {
      throw new UnauthorizedException('User not found');
    }

    const isValid = await bcrypt.compare(currentPassword, user.passwordHash);
    if (!isValid) {
      throw new BadRequestException('Current password is incorrect');
    }

    const passwordHash = await bcrypt.hash(newPassword, 12);
    await this.usersService.update(userId, { passwordHash });

    // Revoke all refresh tokens to force re-login
    await this.prisma.refreshToken.updateMany({
      where: { userId, revokedAt: null },
      data: { revokedAt: new Date() },
    });
  }

  async requestPasswordReset(email: string) {
    const user = await this.usersService.findByEmail(email);
    if (!user) {
      // Don't reveal if email exists
      return { success: true };
    }

    // Generate reset token (valid for 1 hour)
    const resetToken = this.jwtService.sign(
      { sub: user.id, type: 'password-reset' },
      { expiresIn: '1h' },
    );

    // In production, send email with reset link
    // For now, log it (dev only)
    if (this.configService.get('NODE_ENV') !== 'production') {
      console.log(`Password reset token for ${email}: ${resetToken}`);
    }

    return { success: true };
  }

  async resetPassword(token: string, newPassword: string) {
    try {
      const payload = this.jwtService.verify(token);
      if (payload.type !== 'password-reset') {
        throw new UnauthorizedException('Invalid token type');
      }

      const passwordHash = await bcrypt.hash(newPassword, 12);
      await this.usersService.update(payload.sub, { passwordHash });

      // Revoke all refresh tokens
      await this.prisma.refreshToken.updateMany({
        where: { userId: payload.sub, revokedAt: null },
        data: { revokedAt: new Date() },
      });

      return { success: true };
    } catch {
      throw new UnauthorizedException('Invalid or expired reset token');
    }
  }

  private async generateTokens(user: any): Promise<Tokens> {
    const payload: TokenPayload = {
      sub: user.id,
      email: user.email,
      role: user.role,
      companyId: user.companyId,
      clientId: user.clientId,
    };

    const accessToken = this.jwtService.sign(payload);

    const refreshToken = this.jwtService.sign(
      { ...payload, type: 'refresh' },
      {
        secret: this.configService.get('JWT_REFRESH_SECRET'),
        expiresIn: this.configService.get('JWT_REFRESH_EXPIRES_IN') || '7d',
      },
    );

    return { accessToken, refreshToken };
  }

  private async saveRefreshToken(userId: string, token: string) {
    const expiresIn = this.configService.get('JWT_REFRESH_EXPIRES_IN') || '7d';
    const expiresAt = new Date(Date.now() + this.parseExpiration(expiresIn));

    await this.prisma.refreshToken.create({
      data: {
        token,
        userId,
        expiresAt,
      },
    });
  }

  private parseExpiration(exp: string): number {
    const match = exp.match(/^(\d+)([smhd])$/);
    if (!match) return 7 * 24 * 60 * 60 * 1000; // 7 days default

    const value = parseInt(match[1], 10);
    const unit = match[2];

    switch (unit) {
      case 's': return value * 1000;
      case 'm': return value * 60 * 1000;
      case 'h': return value * 60 * 60 * 1000;
      case 'd': return value * 24 * 60 * 60 * 1000;
      default: return 7 * 24 * 60 * 60 * 1000;
    }
  }

  private sanitizeUser(user: any) {
    const { passwordHash, refreshTokens, ...sanitized } = user;
    return sanitized;
  }
}